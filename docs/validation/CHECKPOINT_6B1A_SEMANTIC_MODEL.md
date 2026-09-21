# Checkpoint 6B-1A — Semantic Model Validation

## Result

PASS — the PBIP semantic metadata is hardened for governed measure development. No business measures, report pages, visuals, SQL objects, or publishing changes were introduced.

## Validation Summary

| Check | Expected | Result | Status |
|---|---:|---:|---|
| Visible business tables | 10 | 10 | PASS |
| Hidden Auto Date/Time tables | 0 | 0 | PASS |
| Relationships | 7 | 7 | PASS |
| Bidirectional relationships | 0 | 0 | PASS |
| Many-to-many relationships | 0 | 0 | PASS |
| Inactive relationships | 0 | 0 | PASS |
| Measures | 0 | 0 | PASS |
| Report pages | 1 | 1 | PASS |
| Visuals | 0 | 0 | PASS |
| `CohortRetention` connected | No | No | PASS |
| `CohortRevenue` connected | No | No | PASS |

## Auto Date/Time and Date Table

- `__PBI_TimeIntelligenceEnabled` equals `0`.
- The model contains no `DateTableTemplate`, `LocalDateTable`, automatic date relationship, or date variation reference.
- `analytics DimDate` is the only date table, has `dataCategory: Time`, and uses `FullDate` as its key date column.
- `FullDate` contains 739 distinct, nonblank SQL dates from 2009-12-01 through 2011-12-09; expected inclusive day count is 739, confirming continuity.
- `MonthName` sorts by `MonthNumber`; `DayName` sorts by `DayOfWeekNumber`.

## Relationship Validation

All relationships are active M:1 and use single-direction filtering:

1. `FactTransaction[DateKey]` → `DimDate[DateKey]`
2. `FactTransaction[CustomerKey]` → `DimCustomer[CustomerKey]`
3. `FactTransaction[ProductKey]` → `DimProduct[ProductKey]`
4. `FactTransaction[CountryKey]` → `DimCountry[CountryKey]`
5. `CustomerRFM[CustomerKey]` → `DimCustomer[CustomerKey]`
6. `CustomerCohort[CustomerKey]` → `DimCustomer[CustomerKey]`
7. `CustomerRepeatBehavior[CustomerKey]` → `DimCustomer[CustomerKey]`

The customer summary sources remain one row per customer in SQL. Their model relationships use M:1 rather than 1:1 because Power BI enforces bidirectional filtering on 1:1 relationships. This preserves safe dimension-to-summary filtering and removes ambiguous propagation among customer-level analytical tables.

There are no bidirectional paths, many-to-many relationships, ambiguous active paths, or unsafe relationships to the cohort summary tables.

## Grain and Disconnection Checks

- `CustomerRFM`: one row per `CustomerKey`.
- `CustomerCohort`: one row per `CustomerKey`.
- `CustomerRepeatBehavior`: one row per `CustomerKey`.
- `CohortRetention`: one row per `AcquisitionCohort × CohortIndex`; disconnected.
- `CohortRevenue`: one row per `AcquisitionCohort × CohortIndex`; disconnected.

## Metadata Hygiene Checks

- 39 technical, key, lineage, data-quality, scoring-helper, or observation-status columns are hidden.
- Identifiers and nonadditive numeric attributes use `summarizeBy: none`.
- Only approved additive facts retain Sum: transaction quantity and line amount, plus cohort revenue and orders.
- Neutral date, timestamp, decimal, integer, and percentage formats are applied without inventing a reporting currency.

## Load Validation

Tabular Editor loaded `definition/model.tmdl` in validation mode and exited successfully with code 0 and no parser or model-load errors. The report definition remains one blank page with zero visuals and was not edited.

## Scope Control

- No DAX business measure was created.
- No report page or visual was created or changed.
- No SQL or analytical source artifact was changed.
- No publish, push, or 6B-1A commit was performed.
