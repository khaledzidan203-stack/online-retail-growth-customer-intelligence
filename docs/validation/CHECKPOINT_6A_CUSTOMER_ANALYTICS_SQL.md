# Checkpoint 6A Customer Analytics SQL Validation

## Result

**PASS — 35 of 35 validation metrics passed.**

The publication pipeline loaded validated Python outputs into SQL Server without recreating RFM scoring, segmentation, cohort assignment, retention, or repeat-purchase logic in SQL.

## Published objects and row counts

| Object | Rows | Result |
|---|---:|---|
| `analytics.CustomerRFM` | 5,852 | PASS |
| `analytics.CustomerCohort` | 5,852 | PASS |
| `analytics.CustomerRepeatBehavior` | 5,852 | PASS |
| `analytics.CohortRetention` | 325 | PASS |
| `analytics.CohortRevenue` | 325 | PASS |
| `analytics.vw_Customer360` | 5,852 | PASS |

## RFM reconciliation

- Monetary total: 17,125,672.047 — PASS.
- Frequency total: 36,597 — PASS.
- Segment customer total: 5,852 — PASS.
- Champions 1,261; Loyal Customers 594; Potential Loyalists 716; New Customers 78; Promising 455; Need Attention 409; At Risk 709; Hibernating 681; Lost 949 — all PASS.
- Unclassified customers: 0 — PASS.
- Reference dates other than 2011-12-10: 0 — PASS.

## Cohort reconciliation

- Month 0 cohort sizes sum to 5,852 — PASS.
- Month 0 cells where ActiveCustomers differs from CohortSize or retention differs from 100%: 0 — PASS.
- CohortRetention and CohortRevenue grain mismatches: 0 — PASS.
- Incorrect CustomerCohort left-boundary flags: 0 — PASS.
- Future unobserved cells remain absent; partial-observation flags are loaded from the approved cohort outputs.

## Repeat and customer-key reconciliation

- Repeat customers: 4,234 — PASS.
- Non-repeat customers: 1,618 — PASS.
- DimCustomer rows: 5,942; published eligible-customer rows: 5,852.
- Unmapped published customers: 0.
- Broken CustomerRFM, CustomerCohort, or CustomerRepeatBehavior foreign keys: 0.
- Customer population mismatches among the three customer-level tables: 0.
- Duplicate CustomerKey or CustomerID values in all three customer tables: 0.
- Anonymous or blank customer leakage: 0.

The 90 DimCustomer members outside the eligible merchandise-sales population are deliberately absent rather than being assigned fabricated analytical attributes.

## Customer360 validation

`analytics.vw_Customer360` contains 5,852 rows with zero duplicate CustomerKey or CustomerID values. The view joins only one-to-one customer objects and does not include FactTransaction.

## Reproducibility evidence

`outputs/checkpoint6a_customer_analytics_sql.json` records the SQL Server connection metadata, SHA-256 hash for every governed source output, all validation results, and overall PASS status. The publisher is idempotent and replaces only the five customer analytical tables.

