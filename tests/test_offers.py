import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from validate_offers import schema_errors, temporal_findings

ROOT = Path(__file__).resolve().parents[1]


def load_json(name: str) -> dict:
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def test_repository_data_matches_strict_schema() -> None:
    assert schema_errors(load_json("offers.json"), load_json("offers.schema.json")) == []


def test_unknown_fields_are_rejected() -> None:
    data = load_json("offers.json")
    data["offers"][0]["made_up"] = True
    assert any("Additional properties" in item for item in schema_errors(data, load_json("offers.schema.json")))


def test_current_data_has_no_temporal_errors_at_retrieval_time() -> None:
    findings = temporal_findings(load_json("offers.json"), datetime(2026, 11, 12, 12, tzinfo=timezone.utc))
    assert not [item for item in findings if item.severity in {"ERROR", "STALE"}]


def test_active_expired_offer_is_error() -> None:
    data = load_json("offers.json")
    offer = copy.deepcopy(data["offers"][0])
    offer["observation"]["expires_at"] = "2026-11-01T00:00:00Z"
    data["offers"] = [offer]
    findings = temporal_findings(data, datetime(2026, 11, 12, tzinfo=timezone.utc))
    assert any(item.severity == "ERROR" and "expired" in item.message for item in findings)


def test_stale_active_offer_is_detected() -> None:
    data = load_json("offers.json")
    offer = copy.deepcopy(data["offers"][1])
    offer["observation"]["last_seen_at"] = "2026-01-01T00:00:00Z"
    data["offers"] = [offer]
    findings = temporal_findings(data, datetime(2026, 11, 12, tzinfo=timezone.utc))
    assert any(item.severity == "STALE" for item in findings)

