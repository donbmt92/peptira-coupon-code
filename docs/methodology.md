# Verification methodology

## Evidence levels

1. **Source observed**: text was visible on a named page at a recorded time. This proves only what the page displayed.
2. **Publisher reported**: the publisher says an offer was tested or verified. This is a claim attributable to the publisher.
3. **Independently checkout verified**: an auditor reproduced the discount in checkout and preserved evidence without completing a purchase. No current record in this repository has this level.

The validator prevents a record from claiming the third level while its independent-checkout flag is false.

## Collection

- Record the canonical source URL and UTC retrieval time.
- Preserve the exact sentence that supports the code, value, conditions, expiry, or verification claim.
- Store unknown fields as `null`, an empty list, or explanatory text; never infer missing terms.
- Treat search-indexed snippets as lower-confidence historical evidence when the live page conflicts.
- Do not log in, bypass CAPTCHA, purchase, or automatically publish updates.

## Status rules

- `active`: displayed as current and not known to be expired at the observation time.
- `expired`: a stated end time has passed or the source explicitly labels it expired.
- `unclear`: terms or current status cannot be responsibly determined.

An active record becomes stale after its record-specific threshold. Staleness does not prove expiry; it means the page needs human review.

## Calculation assumptions

Percentage discounts are sequential and rounded to cents after every step. For subtotal `S` and percentages `p1...pn`, the unrounded final amount is:

`S × (1 - p1/100) × ... × (1 - pn/100)`

Fixed discounts cannot reduce the subtotal below zero. Tax, shipping, BOGO allocation, item exclusions, minimum quantities, and merchant rounding are not guessed. Unsupported discount types raise an error.

## Human review checklist

1. Open the source and compare the visible wording to `sources[].evidence`.
2. Confirm dates, timezone, eligible items, minimums, payment method, and stacking terms.
3. Change status and timestamps; do not overwrite historical observations without explanation.
4. Run schema validation and tests.
5. Publish only through a reviewed commit or pull request.

