# Checkpoint 6B-1B — Governed DAX Validation

## Result

PASS — all 50 measures load successfully, use the approved governed populations, and match the corresponding SQL definitions and runtime DAX results. Checkpoint 6B-1C re-homed every measure to `_Measures` without changing any DAX expression or validated result.

## Scope Checks

| Check | Result |
|---|---|
| Measures created | 50 |
| Calculated columns or tables added | 0 |
| Relationships changed during 6B-1B | 0 |
| Report pages created or changed | 0 |
| Visuals created or changed | 0 |
| SQL objects changed | 0 |
| Auto-date tables | 0 |
| Measures owned by `_Measures` | 50 |
| Measures owned by business tables | 0 |
| `_Measures` relationships | 0 |
| `_Measures` business rows | 0 |

## Measure Organization

| Display folder | Measures |
|---|---:|
| 01 Core Sales | 2 |
| 02 Orders & Units | 3 |
| 03 Customers | 7 |
| 04 Cancellation | 5 |
| 05 Time Intelligence | 9 |
| 06 RFM | 9 |
| 07 Cohort & Retention | 7 |
| 08 Data Quality & Utility | 8 |
| **Total** | **50** |

## SQL Baseline Reconciliation

A read-only query against local `OnlineRetailAnalytics` independently reproduced the governed baselines used by the DAX expressions.

| Measure | SQL result | Required result | Definition match | Runtime DAX |
|---|---:|---:|---|---|
| Sales Revenue | 19,701,685.507 | 19,701,685.507 | PASS | PASS |
| Units Sold | 11,221,960 | 11,221,960 | PASS | PASS |
| Orders | 39,519 | 39,519 | PASS | PASS |
| Average Order Value | 498.5370 | ≈498.54 | PASS | PASS |
| Average Units per Order | 283.9637 | ≈283.96 | PASS | PASS |
| Sales Customers | 5,852 | 5,852 | PASS | PASS |
| Known Customer Revenue | 17,125,672.047 | 17,125,672.047 | PASS | PASS |
| Revenue per Known Customer | 2,926.4648 | ≈2,926.47 | PASS | PASS |
| Orders per Known Customer | 6.2538 | ≈6.25 | PASS | PASS |
| Repeat Customers | 4,234 | 4,234 | PASS | PASS |
| One-Time Customers | 1,618 | 1,618 | PASS | PASS |
| Repeat Customer Rate | 72.3513% | ≈72.35% | PASS | PASS |
| Cancellation Value | 719,692.940 | 719,692.94 | PASS | PASS |
| Cancellation Units | 469,882 | 469,882 | PASS | PASS |
| Cancellation Invoices | 7,406 | 7,406 | PASS | PASS |
| Customers with Cancellations | 2,445 | 2,445 | PASS | PASS |
| Cancellation Value Rate | 3.524213% | ≈3.5242% | PASS | PASS |
| RFM Customers | 5,852 | 5,852 | PASS | PASS |
| RFM Revenue | 17,125,672.047 | 17,125,672.047 | PASS | PASS |
| Canonical Transaction Rows | 1,044,848 | 1,044,848 | PASS | PASS |
| Sales Eligible Rows | 1,015,091 | 1,015,091 | PASS | PASS |
| Anonymous Sales Revenue | 2,576,013.460 | 2,576,013.46 | PASS | PASS |
| Anonymous Sales Revenue % | 13.0751% | ≈13.08% | PASS | PASS |
| Duplicate Flagged Revenue | 57,092.820 | Approved sensitivity | PASS | PASS |
| Duplicate Revenue Impact % | 0.2898% | Derived sensitivity | PASS | PASS |
| Operational Adjustment Rows | 3,392 | Approved class count | PASS | PASS |
| DQ Review Rows | 0 | 0 | PASS | PASS |

## Static Expression Validation

- Sales, units, and orders intersect current filters with `IsSalesEligible = TRUE`.
- Customer revenue and counts use only `IsCustomerAnalyticsEligible = TRUE`.
- Repeat measures consume `CustomerRepeatBehavior[HasRepeatPurchase]`; repeat logic is not reconstructed from the fact.
- Cancellation measures use `IsCancellationEligible = TRUE`, absolute values, and known-customer filtering where required. Operational adjustments are excluded by the governed flag.
- RFM measures consume published `CustomerRFM` scores and monetary values. They do not recreate scoring or segmentation.
- Segment totals remove only the `Segment` filter for denominators; segment numerators retain current filter context.
- Cohort measures operate within their disconnected source tables. Retention is a weighted ratio of summed active customers to summed cohort-size exposure across visible cohort-period cells and never sums stored retention rates.
- Time intelligence uses only `DimDate[FullDate]`.
- Utility measures preserve the canonical, anonymous, duplicate, operational-adjustment, and DQ populations.

## Model Load Validation

Tabular Editor 2.28 loaded `definition/model.tmdl` after measure creation and after the `_Measures` alignment, exiting with code 0. Static inspection found exactly 50 measures in the eight governed display folders, all owned by `_Measures`.

## Dedicated Measure Table Alignment

- `_Measures` exists as an unconnected, zero-row import table.
- Its single `Placeholder` text column is hidden and contains no values.
- All 50 measure blocks were moved from their four prior owners into `_Measures`.
- An automated before/after comparison reported `DaxExpressionsChanged=0`.
- Relationship count remained seven before and after; none references `_Measures`.
- The report remains one blank page with zero visuals.

## Runtime Validation

A read-only ADOMD query ran directly against the active local Power BI Analysis Services model after re-homing. Every required SQL ↔ DAX value passed, including explicit zero for `DQ Review Rows`. Additional time-intelligence, RFM, and cohort measures also executed without errors. No report page or visual was used for validation.

## Time-Boundary Warning

The date range starts in December 2009 and ends on 2011-12-09. PY, YoY, YTD, and MTD measures calculate correctly for their filter context, but business comparisons must use equivalent covered periods and must not treat partial 2009 or partial 2011 as full years.
