# Peptira Coupon Verification & Offer Tracker

A small, evidence-led dataset and Python toolkit for recording public Peptira promotions, detecting stale or expired records, and calculating sequential discounts without treating publisher claims as independent checkout proof.

This is an independent project. It is not affiliated with, endorsed by, or operated by Peptira.

## Why this exists

Coupon pages can remain indexed after a promotion ends, and stacked percentages are often described additively. This repository keeps timestamped evidence and makes its assumptions testable. It remains useful without any affiliate link: the JSON history, strict schema, validator, calculator, and tests are all local and reusable.

## Current data status

Last source retrieval: **2026-11-12 11:14:29 UTC**.

- The live source displayed `PEPTIDESAVE10` with a selected-item Veterans Day BOGO and an extra 10% where accepted, described as running November 11–13, 2026.
- The source also displayed free U.S. shipping on qualifying orders of $250 or more.
- Eligible BOGO items and the exact November 13 cutoff time/timezone were not stated.
- Peptigator labeled the records verified; this repository did **not** independently test checkout.
- An expired September search-index snapshot still described a 35% + 10% + 5% stack. It is retained only as history.

Always confirm eligibility and the final amount before payment. A source observation is not a guarantee that an offer still works.

## Historical observation worth checking

The expired Labor Day copy described 35%, 10%, and 5% discounts as “up to 50%.” If applied sequentially to $100:

```text
$100.00 - 35% = $65.00
$65.00  - 10% = $58.50
$58.50  -  5% = $55.58 after cent rounding
Effective discount = 44.42%
```

The exact unrounded effective rate is 44.425%. Merchant rules may differ, so the repository records the conflict instead of asserting how that historical checkout behaved.

## Install

Requires Python 3.12 or newer.

### Git Bash on Windows

Git Bash requires forward slashes in Windows paths and uses the POSIX-style
activation script:

```bash
cd 'E:/Backup_D/2026/peptide/dev/peptide-price/peptira-offer-tracker'
pwd
test -f pyproject.toml || { echo "Wrong directory"; exit 1; }
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -e ".[test]"
```

### PowerShell on Windows

```powershell
Set-Location -LiteralPath 'E:\Backup_D\2026\peptide\dev\peptide-price\peptira-offer-tracker'
if (-not (Test-Path -LiteralPath 'pyproject.toml')) { throw 'Wrong directory' }
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Run the commands below only after `pwd` or `Get-Location` shows the project
directory. Running `pytest` from the home directory can make it scan unrelated
files under the user profile.

## Use the calculator

Apply percentage discounts in the order supplied:

```bash
python -m discount_calculator 100 --percent 35 --percent 10 --percent 5
```

Expected summary:

```text
Final subtotal: $55.58
Effective discount: 44.420%
```

The Python API also accepts eligibility conditions:

```python
from discount_calculator import calculate_sequential

result = calculate_sequential(
    "120.00",
    [{
        "name": "ACH offer",
        "kind": "percent",
        "value": 5,
        "conditions": {
            "min_subtotal": 100,
            "payment_methods": ["ACH"],
            "regions": ["US"],
        },
    }],
    context={"payment_method": "ACH", "region": "US"},
)
print(result.final_subtotal)  # 114.00
```

BOGO, shipping, tax, and product-allocation effects are not guessed. The calculator raises an error when asked to reduce them to a subtotal discount without itemized data.

## Validate data and run tests

```bash
python -m validate_offers --fail-on-stale
python -m pytest
```

Validation covers the strict JSON schema, duplicate IDs, date ordering, active-but-expired records, stale active records, and contradictory verification fields. A weekly GitHub Actions schedule runs the same checks. It never changes offer status or publishes scraped updates.

## Data and methodology

- [`data/offers.json`](data/offers.json): machine-readable observations
- [`data/offers.schema.json`](data/offers.schema.json): strict JSON Schema
- [`docs/offer-history.md`](docs/offer-history.md): human-readable history
- [`docs/methodology.md`](docs/methodology.md): evidence levels and calculation assumptions
- [`research/source-ledger.json`](research/source-ledger.json): source evidence, retrieval times, and conflicts

Percentage discounts are applied sequentially and rounded to cents after each step. Fixed discounts cannot reduce the subtotal below zero. Unknown terms stay unknown.

## Limitations

- Promotional terms can change without notice.
- No current offer has been independently verified at checkout by this project.
- Search snippets can be stale or wrong.
- The data does not establish product quality, regulatory status, merchant reliability, or fitness for any use.
- This repository provides no medical, treatment, dosing, or human-use advice.

## Source and affiliate disclosure

Primary observation source: [Peptigator's Peptira offer page](https://peptigator.com/coupon/peptira?utm_source=github&utm_medium=referral&utm_campaign=peptira_offer_tracker), retrieved 2026-11-12. This is an affiliate-tagged reference link; the site owner may receive compensation if a visitor follows it and completes a qualifying action. That relationship is separate from Peptira, and it does not convert publisher-reported verification into independent verification.

See the source ledger for exact evidence and retrieval method.

## Contributing

Submit evidence as a reviewed pull request. Include the public URL, UTC retrieval time, exact supporting text, conditions, and verification level. Do not submit personal checkout data, automate purchases, or mark an offer independently verified without reproducible evidence.

