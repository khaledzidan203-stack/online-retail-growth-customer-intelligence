# Checkpoint 5C Cohort Validation

## Result

**PASS**

The cohort pipeline reads only governed SQL records where `IsCustomerAnalyticsEligible = 1` and aggregates distinct eligible invoices before calculating cohorts.

## Reconciliation and structural checks

| Check | Result |
|---|---|
| Eligible known customers | 5,852 — PASS |
| Unique customer rows | 5,852 — PASS |
| Customers with exactly one acquisition cohort | 5,852 — PASS |
| Cohort sizes sum | 5,852 — PASS |
| Month 0 ActiveCustomers equals CohortSize | All 25 cohorts — PASS |
| Month 0 retention | 100% for all cohorts — PASS |
| Negative CohortIndex | 0 — PASS |
| RetentionRate above 100% | 0 — PASS |
| Cohort revenue | 17,125,672.047 — PASS |
| Cohort orders | 36,597 — PASS |
| Anonymous customer IDs | 0 — PASS |

Revenue reconciles within 0.0001 tolerance with an observed difference of zero. Customer and order measures reconcile exactly. Because the source query filters `IsCustomerAnalyticsEligible = 1`, cancellations and other ineligible transaction classes do not enter the output.

## Distinct-customer behavior

`ActiveCustomers` uses `COUNT(DISTINCT CustomerID)` at AcquisitionCohort × CohortIndex. The pipeline first reduces eligible facts to distinct customer invoices, ensuring multiple lines or multiple invoices in one activity month do not multiply the retained-customer count.

## Partial-period validation

- 2009-12 is explicitly flagged as the left-boundary cohort.
- 2011-12 activity cells are marked `PARTIAL_THROUGH_2011-12-09`.
- Future cohort cells are absent rather than zero-filled.
- Observed complete months with no activity are retained as zero.
- Weighted and median checkpoint metrics exclude partial December 2011 cells.

## Downstream grain

- `customer_repeat_timing.csv`: one row per governed known customer.
- `cohort_customer_retention.csv`: one row per observed AcquisitionCohort × CohortIndex.
- `cohort_revenue.csv`: the same cohort-period grain with revenue and order measures.

