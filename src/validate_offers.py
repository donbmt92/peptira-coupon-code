"""Strict schema, expiration, and staleness validation for offer records."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


@dataclass(frozen=True)
class Finding:
    severity: str
    offer_id: str
    message: str


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Datetime must include timezone: {value}")
    return parsed.astimezone(timezone.utc)


def schema_errors(document: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path))
    return [f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}" for error in errors]


def temporal_findings(document: dict[str, Any], now: datetime) -> list[Finding]:
    findings: list[Finding] = []
    seen_ids: set[str] = set()
    for offer in document.get("offers", []):
        offer_id = offer.get("id", "<missing-id>")
        if offer_id in seen_ids:
            findings.append(Finding("ERROR", offer_id, "duplicate offer id"))
        seen_ids.add(offer_id)

        observation = offer.get("observation", {})
        try:
            first_seen = parse_datetime(observation["first_seen_at"])
            last_seen = parse_datetime(observation["last_seen_at"])
        except (KeyError, TypeError, ValueError) as exc:
            findings.append(Finding("ERROR", offer_id, f"invalid observation datetime: {exc}"))
            continue

        if last_seen < first_seen:
            findings.append(Finding("ERROR", offer_id, "last_seen_at precedes first_seen_at"))

        expires_value = observation.get("expires_at")
        if expires_value:
            try:
                expires_at = parse_datetime(expires_value)
            except ValueError as exc:
                findings.append(Finding("ERROR", offer_id, str(exc)))
            else:
                if offer.get("status") == "active" and expires_at <= now:
                    findings.append(Finding("ERROR", offer_id, f"active offer expired at {expires_value}"))
                if offer.get("status") == "expired" and expires_at > now:
                    findings.append(Finding("WARNING", offer_id, "offer is marked expired before expires_at"))

        stale_after = observation.get("stale_after_days")
        if offer.get("status") == "active" and isinstance(stale_after, int):
            stale_at = last_seen + timedelta(days=stale_after)
            if stale_at < now:
                findings.append(Finding("STALE", offer_id, f"not observed since {observation['last_seen_at']}"))

        verification = offer.get("verification", {})
        if verification.get("level") == "independently_checkout_verified" and not verification.get(
            "independently_checkout_verified"
        ):
            findings.append(Finding("ERROR", offer_id, "verification level contradicts checkout flag"))
    return findings


def validate_files(data_path: Path, schema_path: Path, *, now: datetime | None = None) -> tuple[list[str], list[Finding]]:
    document = json.loads(data_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = schema_errors(document, schema)
    findings = [] if errors else temporal_findings(document, now or datetime.now(timezone.utc))
    return errors, findings


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate Peptira offer records")
    parser.add_argument("--data", type=Path, default=root / "data" / "offers.json")
    parser.add_argument("--schema", type=Path, default=root / "data" / "offers.schema.json")
    parser.add_argument("--as-of", help="ISO-8601 time override for reproducible checks")
    parser.add_argument("--fail-on-stale", action="store_true")
    args = parser.parse_args()

    now = parse_datetime(args.as_of) if args.as_of else datetime.now(timezone.utc)
    errors, findings = validate_files(args.data, args.schema, now=now)
    for error in errors:
        print(f"ERROR schema: {error}")
    for finding in findings:
        print(f"{finding.severity} {finding.offer_id}: {finding.message}")

    fatal = bool(errors) or any(item.severity == "ERROR" for item in findings)
    if args.fail_on_stale:
        fatal = fatal or any(item.severity == "STALE" for item in findings)
    if fatal:
        return 1
    print(f"PASS: {len(findings)} non-fatal finding(s); validated at {now.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

