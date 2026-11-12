"""Deterministic sequential-discount calculator.

Only cart-subtotal percentage and fixed-amount discounts are calculated. BOGO,
shipping, tax, and product-specific allocations require data this module does
not guess.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Mapping

CENT = Decimal("0.01")


class DiscountError(ValueError):
    """Raised when a discount cannot be safely evaluated."""


@dataclass(frozen=True)
class AppliedDiscount:
    name: str
    kind: str
    amount: Decimal
    subtotal_after: Decimal


@dataclass(frozen=True)
class CalculationResult:
    original_subtotal: Decimal
    final_subtotal: Decimal
    total_discount: Decimal
    applied: tuple[AppliedDiscount, ...]
    skipped: tuple[str, ...]

    @property
    def effective_percent(self) -> Decimal:
        if self.original_subtotal == 0:
            return Decimal("0")
        return (self.total_discount / self.original_subtotal * 100).quantize(
            Decimal("0.001"), rounding=ROUND_HALF_UP
        )


def money(value: Decimal | str | int | float) -> Decimal:
    """Convert a value to non-negative, cent-rounded Decimal currency."""
    try:
        amount = Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
    except Exception as exc:  # Decimal raises several input-specific errors.
        raise DiscountError(f"Invalid money value: {value!r}") from exc
    if amount < 0:
        raise DiscountError("Money values cannot be negative")
    return amount


def _eligible(discount: Mapping[str, Any], subtotal: Decimal, context: Mapping[str, Any]) -> tuple[bool, str]:
    conditions = discount.get("conditions", {})
    minimum = conditions.get("min_subtotal")
    if minimum is not None and subtotal < money(minimum):
        return False, f"subtotal is below {money(minimum)}"

    for key in ("payment_method", "region"):
        allowed = conditions.get(f"{key}s", [])
        actual = context.get(key)
        if allowed and actual not in allowed:
            return False, f"{key} {actual!r} is not eligible"
    return True, ""


def calculate_sequential(
    subtotal: Decimal | str | int | float,
    discounts: Iterable[Mapping[str, Any]],
    *,
    context: Mapping[str, Any] | None = None,
) -> CalculationResult:
    """Apply eligible discounts in list order, rounding after each step.

    Each discount needs ``name``, ``kind`` (``percent`` or ``fixed``), and
    ``value``. Optional conditions support ``min_subtotal``,
    ``payment_methods``, and ``regions``. Ineligible discounts are reported as
    skipped. Unsupported kinds raise instead of silently estimating savings.
    """
    original = money(subtotal)
    current = original
    applied: list[AppliedDiscount] = []
    skipped: list[str] = []
    supplied_context = context or {}

    for index, discount in enumerate(discounts, start=1):
        name = str(discount.get("name") or f"discount-{index}")
        kind = discount.get("kind")
        eligible, reason = _eligible(discount, current, supplied_context)
        if not eligible:
            skipped.append(f"{name}: {reason}")
            continue

        raw_value = discount.get("value")
        if kind == "percent":
            value = Decimal(str(raw_value))
            if not Decimal("0") <= value <= Decimal("100"):
                raise DiscountError(f"{name}: percent must be between 0 and 100")
            subtotal_after = (current * (Decimal("100") - value) / 100).quantize(
                CENT, rounding=ROUND_HALF_UP
            )
            amount = current - subtotal_after
        elif kind == "fixed":
            amount = min(current, money(raw_value))
            subtotal_after = current - amount
        else:
            raise DiscountError(
                f"{name}: unsupported kind {kind!r}; BOGO, shipping, and tax require itemized data"
            )

        current = subtotal_after
        applied.append(AppliedDiscount(name, kind, amount, current))

    return CalculationResult(
        original_subtotal=original,
        final_subtotal=current,
        total_discount=original - current,
        applied=tuple(applied),
        skipped=tuple(skipped),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate sequential cart discounts")
    parser.add_argument("subtotal", help="Cart subtotal, for example 100.00")
    parser.add_argument("--percent", action="append", default=[], help="Percent discount; repeat in application order")
    parser.add_argument("--fixed", action="append", default=[], help="Fixed discount; applied after percentages")
    parser.add_argument("--json", type=Path, help="JSON file containing a list of discount objects")
    parser.add_argument("--payment-method")
    parser.add_argument("--region")
    args = parser.parse_args()

    discounts: list[Mapping[str, Any]] = []
    if args.json:
        discounts.extend(json.loads(args.json.read_text(encoding="utf-8")))
    discounts.extend(
        {"name": f"{value}%", "kind": "percent", "value": value}
        for value in args.percent
    )
    discounts.extend(
        {"name": f"{value} fixed", "kind": "fixed", "value": value}
        for value in args.fixed
    )
    result = calculate_sequential(
        args.subtotal,
        discounts,
        context={"payment_method": args.payment_method, "region": args.region},
    )
    print(f"Original subtotal: ${result.original_subtotal}")
    for item in result.applied:
        print(f"{item.name}: -${item.amount} -> ${item.subtotal_after}")
    for item in result.skipped:
        print(f"Skipped: {item}")
    print(f"Final subtotal: ${result.final_subtotal}")
    print(f"Effective discount: {result.effective_percent}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

