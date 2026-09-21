# Checkpoint 5B RFM Validation

## Result

**PASS**

The RFM pipeline reads only SQL rows where `IsCustomerAnalyticsEligible = 1` and creates exactly one output row per governed known customer.

## Reconciliation

| Check | RFM output | Governed SQL | Result |
|---|---:|---:|---|
| Distinct customers | 5,852 | 5,852 | PASS |
| Known-customer revenue | 17,125,672.047 | 17,125,672.047 | PASS |
| Distinct customer orders | 36,597 | 36,597 | PASS |
| Units | 10,532,303 | 10,532,303 | PASS |
| Unique customer rows | 5,852 | 5,852 | PASS |
| Valid R/F/M scores | All 1–5 | All 1–5 | PASS |
| Named segment assignment | 5,852 | 5,852 | PASS |
| Null or unclassified segments | 0 | 0 | PASS |

Revenue reconciles within a 0.0001 numeric tolerance; the observed difference is zero. Integer measures reconcile exactly.

## Quality review

- Champions average 20.0 recency days, 17.28 orders, and 9,212.07 monetary value, consistent with the intended recent/high-frequency/high-value behavior.
- Lost customers average 553.5 recency days and 1.25 orders; Hibernating customers average 315.9 days and 1.38 orders.
- At Risk customers average 360.0 recency days but retain 5.49 average orders and 2,159.50 average monetary value, distinguishing previously engaged customers from low-engagement dormant groups.
- New Customers contain 78 recent one-order customers; no customers are unclassified.
- Segment shares are intentionally unequal because identical Frequency values are never split merely to balance bins.

## Reproducibility and downstream readiness

- Reference date: 2011-12-10, derived as one day after the maximum eligible invoice date.
- Scoring boundaries and tie logic are machine-readable in `outputs/rfm_score_boundaries.json`.
- Customer output grain: one row per known customer, suitable for a future `analytics.CustomerRFM` table.
- RFM has not been loaded into SQL in this checkpoint.

