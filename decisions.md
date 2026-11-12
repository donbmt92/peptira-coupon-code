# Decision log

## 2026-11-12 — Proceed with a utility repository

**Decision:** Build the project.

**Reason:** It has independent utility as a timestamped ledger, strict schema, stale/expiry checker, and discount calculator. Removing the affiliate link does not remove that utility.

## Keep the project isolated

**Decision:** Place the deliverable in `peptira-offer-tracker/` and do not modify the existing Next.js application.

**Reason:** The workspace already contains unrelated modified and untracked files. The requested stack is Python/JSON/Markdown, so no Next.js API or convention is involved.

## Do not perform checkout verification

**Decision:** Classify all current verification as publisher-reported.

**Reason:** No checkout interaction, account access, or purchase was authorized or needed. A publisher's “verified” label is not independent evidence.

## Preserve the expired indexed offer

**Decision:** Keep the September Labor Day stack as expired historical data.

**Reason:** It documents search-index staleness and a material arithmetic conflict without presenting the offer as current.

## Do not convert BOGO to a percentage

**Decision:** Store its numeric value as unknown.

**Reason:** Effective savings depend on eligible item prices and cart composition.

## Fail scheduled checks on stale active records

**Decision:** Run `validate_offers --fail-on-stale` weekly.

**Reason:** Automation should request human review, not scrape and publish unverified changes.

