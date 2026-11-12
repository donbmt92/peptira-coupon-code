from decimal import Decimal

import pytest

from discount_calculator import DiscountError, calculate_sequential


def test_sequential_percentages_are_not_additive() -> None:
    result = calculate_sequential(
        "100.00",
        [
            {"name": "catalog", "kind": "percent", "value": 35},
            {"name": "code", "kind": "percent", "value": 10},
            {"name": "ACH", "kind": "percent", "value": 5},
        ],
    )
    assert result.final_subtotal == Decimal("55.58")
    assert result.total_discount == Decimal("44.42")
    assert result.effective_percent == Decimal("44.420")


def test_rounds_after_each_discount() -> None:
    result = calculate_sequential(
        "19.99",
        [
            {"name": "first", "kind": "percent", "value": 10},
            {"name": "second", "kind": "percent", "value": 5},
        ],
    )
    assert [item.amount for item in result.applied] == [Decimal("2.00"), Decimal("0.90")]
    assert result.final_subtotal == Decimal("17.09")


def test_fixed_discount_cannot_make_total_negative() -> None:
    result = calculate_sequential("10", [{"name": "credit", "kind": "fixed", "value": 25}])
    assert result.final_subtotal == Decimal("0.00")


def test_ineligible_condition_is_reported() -> None:
    result = calculate_sequential(
        "80",
        [
            {
                "name": "ACH-only",
                "kind": "percent",
                "value": 5,
                "conditions": {"min_subtotal": 100, "payment_methods": ["ACH"]},
            }
        ],
        context={"payment_method": "card"},
    )
    assert not result.applied
    assert "below" in result.skipped[0]


def test_bogo_is_not_guessed() -> None:
    with pytest.raises(DiscountError, match="unsupported kind"):
        calculate_sequential("100", [{"name": "BOGO", "kind": "bogo", "value": None}])

