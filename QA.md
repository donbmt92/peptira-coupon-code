# Independent QA report

Audit date: 2026-11-12. Status meanings: PASS = supported by evidence; FAIL = requirement not met; UNVERIFIED = cannot be established from available evidence.

| Area | Status | Evidence |
|---|---|---|
| Code execution | PASS | Local pytest and CLI results are recorded in the delivery report; calculator tests cover sequential rounding, fixed floors, conditions, and unsupported BOGO. |
| JSON schema integrity | PASS | Draft 2020-12 schema uses `additionalProperties: false`; repository data validates locally. |
| Expiration logic | PASS | Tests detect active records whose exact `expires_at` has passed; records with ambiguous cutoff retain textual expiry instead of a fabricated timestamp. |
| Stale-data logic | PASS | Active records have explicit thresholds; `--fail-on-stale` is enabled in the workflow. |
| Factual accuracy | PASS | Live-source statements have timestamped exact evidence; stale September content is marked expired and conflicting. |
| Checkout functionality of PEPTIDESAVE10 | UNVERIFIED | No independent checkout test was performed. The “verified” statement belongs to Peptigator. |
| README usability | PASS | README includes setup, examples, current status, history, assumptions, limitations, sources, and disclosure. |
| Originality and added value | PASS | The ledger schema, validation logic, tests, and sequential arithmetic are original utility, not a copy of the source page. |
| Affiliate disclosure | PASS | Disclosure is adjacent to the only affiliate-tagged reference link. |
| GitHub Acceptable Use posture | PASS | No fake engagement, issue spam, automated publishing, or third-party outreach is included. |
| Google spam-policy risk | PASS with risk | The project is useful without its outbound link and avoids fabricated metrics; risk remains if maintainers later mass-produce near-identical merchant repositories. |
| Links and UTM parameters | PASS | The README contains one Peptigator link with `utm_source=github`, `utm_medium=referral`, and `utm_campaign=peptira_offer_tracker`. |
| Merchant affiliation | PASS | README explicitly says the project is not affiliated with Peptira. |
| Medical/human-use guidance | PASS | No dosing, treatment, or human-use advice is provided. |
| Google rankings and traffic potential | UNVERIFIED | SERP observations do not prove demand or future ranking. Search Console data is required after publication. |
| GitHub Actions execution | UNVERIFIED | Workflow syntax and commands were inspected locally, but GitHub-hosted execution requires publication. |

## Residual risks

- The live BOGO offer may change before publication.
- The source's verification and usage counters cannot be independently audited here.
- Coupon-focused search results may not reward repository-form content.
- A future maintainer could weaken the project by replacing historical evidence or auto-publishing scraped codes.

