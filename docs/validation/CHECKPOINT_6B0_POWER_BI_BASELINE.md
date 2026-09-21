# Checkpoint 6B-0 Power BI Baseline Validation

## Overall result

**PASS WITH REVIEW ITEMS**

The existing PBIP was found at `powerbi/OnlineRetailAnalytics.pbip` and inspected without modification. It points to the sibling semantic model and the semantic model imports the ten expected `analytics` tables from `localhost / OnlineRetailAnalytics`.

## Explicit baseline checks

| Check | Finding | Status |
|---|---|---|
| Expected visible business tables | All 10 present; no additional visible business table | PASS |
| Model serialization | TMDL, compatibility level 1606 | PASS |
| SQL source | `localhost`, database `OnlineRetailAnalytics` | PASS |
| Storage mode | Import on all 10 business tables | PASS |
| Measures | 0 | PASS baseline |
| Report pages | 1 (`Page 1`) | PASS baseline |
| Report visuals | 0 | PASS baseline |
| Business relationships | 7 active relationships | PASS with review |
| Auto-date relationships | 8 active relationships | REVIEW |
| Hidden auto-date objects | 1 template plus 8 LocalDateTable objects | REVIEW |
| Many-to-many relationships | 0 | PASS |
| Bidirectional relationships | 3 customer one-to-one relationships | REVIEW |
| Inactive relationships | 0 | PASS |
| CohortRetention relationships | None | PASS |
| CohortRevenue relationships | None | PASS |
| Summary-table-to-summary-table relationship | None | PASS |
| Key types | Date/Customer/Product/Country keys are consistently int64 across related business tables | PASS |
| Customer analytical grains | One row per customer in RFM, Cohort, and Repeat tables | PASS based on governed SQL source and key metadata |
| Cohort summary grains | AcquisitionCohort × CohortIndex in both summary tables | PASS |

## Relationship validation

The four star-schema relationships are active many-to-one, single-direction relationships from FactTransaction keys to their dimensions. The three customer analytical relationships are active one-to-one and bidirectional. The remaining eight relationships connect dateTime columns to hidden LocalDateTable objects.

No current many-to-many or duplicate relationship path was found. No current relationship joins the two cohort summary facts. The three bidirectional customer relationships are nevertheless marked REVIEW because they allow filters to travel between customer analytical tables and FactTransaction through DimCustomer and can create ambiguity as new relationships are added.

## Date validation

DimDate contains an integer-compatible DateKey and a FullDate imported as dateTime with an underlying Date annotation. All governed calendar attributes, including MonthNumber and YearMonth, exist. MonthName has no sort-by assignment, and the table is not explicitly marked as the model date table.

Auto Date/Time is enabled. The model contains hidden local calendars for DimDate.FullDate, FactTransaction.InvoiceDate, three CustomerRFM dates, CustomerCohort.FirstPurchaseDate, and two CustomerRepeatBehavior dates.

## Grain validation

- CustomerRFM: one eligible known customer per CustomerKey.
- CustomerCohort: one eligible known customer per CustomerKey.
- CustomerRepeatBehavior: one eligible known customer per CustomerKey.
- CohortRetention: one AcquisitionCohort × CohortIndex cell.
- CohortRevenue: one AcquisitionCohort × CohortIndex cell.

The three customer tables are suitable for relationships to DimCustomer at their present validated grains. CohortRetention and CohortRevenue are correctly disconnected in the current baseline.

## Required review before visual development

1. Replace bidirectional customer filtering with a deliberate single-direction design.
2. Adopt DimDate as the sole governed date table and remove Auto Date/Time complexity.
3. Define explicit measures and prevent unsafe implicit aggregation of rates and per-customer fields.
4. Apply column hiding, formats, sorting, and display folders only in an authorized semantic-model checkpoint.
5. Keep PBIP local cache/settings artifacts out of source control.

No PBIP relationship, table, column, measure, page, visual, setting, connection, or TMDL definition was changed in this checkpoint.

