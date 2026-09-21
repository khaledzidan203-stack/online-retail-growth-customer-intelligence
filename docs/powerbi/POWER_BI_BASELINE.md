# Power BI PBIP Baseline

## Scope and project structure

This is a read-only discovery baseline. No PBIP semantic-model or report file was changed.

- PBIP root: `powerbi/OnlineRetailAnalytics.pbip`
- Semantic model: `powerbi/OnlineRetailAnalytics.SemanticModel/`
- Report: `powerbi/OnlineRetailAnalytics.Report/`
- Model format: TMDL, compatibility level 1606; semantic-model definition properties version 4.2.
- Report format: PBIR project definition version 4.0 with report-definition schema 3.3.0.
- Connection: `Sql.Database("localhost", "OnlineRetailAnalytics")`.
- Storage mode: Import for all ten SQL-backed business tables.
- Report baseline: one 1920 × 1080 page named `Page 1`; zero visuals.

The semantic model contains 19 tables: 10 visible SQL-backed business tables and 9 hidden Auto Date/Time objects. It contains zero explicit measures and 15 active relationships.

## Complete table inventory

### Visible business tables

1. `analytics DimDate`
2. `analytics DimCustomer`
3. `analytics DimProduct`
4. `analytics DimCountry`
5. `analytics FactTransaction`
6. `analytics CustomerRFM`
7. `analytics CustomerCohort`
8. `analytics CustomerRepeatBehavior`
9. `analytics CohortRetention`
10. `analytics CohortRevenue`

The `analytics ` prefix is part of each imported Power BI table name.

### Hidden Auto Date/Time tables

1. `DateTableTemplate_c153b24f-6526-4f46-a8db-17fa294b31fc`
2. `LocalDateTable_144d4733-59af-43ac-b2a2-6e81bbb01c7a`
3. `LocalDateTable_16b82e2b-1c77-41d3-85cd-c9045662926d`
4. `LocalDateTable_221a641f-1944-4897-955b-da937da1ef6b`
5. `LocalDateTable_3f018e58-47ff-4a2a-966b-ffc8c45f0791`
6. `LocalDateTable_5dc9f7ea-7882-484f-bb5f-9bd6fb68b423`
7. `LocalDateTable_6199474d-0885-4c1f-a5a8-7f416634e9e4`
8. `LocalDateTable_d8aa6b57-0540-4f9f-aeb1-769a2dfdcdd7`
9. `LocalDateTable_f80d9302-d5f9-4850-9288-0c16fbfb49bd`

The template plus eight LocalDateTable objects confirm that Auto Date/Time is enabled and materially expands the model beyond the ten intended business tables.

## Business-table baseline

All listed columns are currently visible in the model.

| Table | Source and analytical role | Grain and key | Visible columns with TMDL types |
|---|---|---|---|
| `analytics DimDate` | `analytics.DimDate`; Dimension | One calendar date; `DateKey` | DateKey int64; FullDate dateTime; Year, Quarter, MonthNumber, WeekOfYear, DayOfMonth, DayOfWeekNumber int64; MonthName, YearMonth, DayName string |
| `analytics DimCustomer` | `analytics.DimCustomer`; Dimension | One known CustomerID; `CustomerKey` | CustomerKey int64; CustomerID string |
| `analytics DimProduct` | `analytics.DimProduct`; Dimension | One governed StockCode; `ProductKey` | ProductKey int64; StockCode, RepresentativeDescription, ItemClass string |
| `analytics DimCountry` | `analytics.DimCountry`; Dimension | One governed country; `CountryKey` | CountryKey int64; Country string |
| `analytics FactTransaction` | `analytics.FactTransaction`; Transaction Fact | One governed transaction line; `TransactionLineKey` | TransactionLineKey, DateKey, CustomerKey, ProductKey, CountryKey, SourceRowNumber, Quantity, ExactDuplicateGroupSize int64; InvoiceDate dateTime; Price, LineAmount double; SourceSheet, Invoice, LineDescription, ItemClass, TransactionClass, DQReviewReason string; eleven eligibility/classification/duplicate columns boolean |
| `analytics CustomerRFM` | `analytics.CustomerRFM`; Customer Analytical Table | One eligible known customer; `CustomerKey` | CustomerKey, Recency, Frequency, R_Score, F_Score, M_Score, RFM_Total, UnitsPurchased, ActiveLifespanDays int64; CustomerID, RFM_Code, Segment string; ReferenceDate, FirstPurchaseDate, LastPurchaseDate dateTime; Monetary, AverageOrderValue double |
| `analytics CustomerCohort` | `analytics.CustomerCohort`; Customer Analytical Table | One eligible known customer; `CustomerKey` | CustomerKey int64; CustomerID, AcquisitionCohort string; FirstPurchaseDate dateTime; IsLeftBoundaryAffected boolean |
| `analytics CustomerRepeatBehavior` | `analytics.CustomerRepeatBehavior`; Customer Analytical Table | One eligible known customer; `CustomerKey` | CustomerKey, DaysToSecondPurchase int64; CustomerID string; FirstPurchaseDate, SecondPurchaseDate dateTime; HasRepeatPurchase boolean |
| `analytics CohortRetention` | `analytics.CohortRetention`; Cohort Summary Table | AcquisitionCohort × CohortIndex; composite business grain | AcquisitionCohort, ActivityMonth, ObservationStatus string; CohortIndex, CohortSize, ActiveCustomers int64; RetentionRate double; IsLeftBoundaryCohort, IsPartialObservation boolean |
| `analytics CohortRevenue` | `analytics.CohortRevenue`; Cohort Summary Table | AcquisitionCohort × CohortIndex; composite business grain | AcquisitionCohort, ActivityMonth, ObservationStatus string; CohortIndex, CohortSize, Orders int64; Revenue, RevenuePerOriginalCustomer, OrdersPerOriginalCustomer double; IsLeftBoundaryCohort, IsPartialObservation boolean |

## Relationship baseline

TMDL omits properties when they have default values. In this baseline, omitted `isActive` means active, omitted cardinality means many-to-one, and omitted cross-filter behavior means single direction from the one-side (`To`) to the many-side (`From`).

| # | From table/column | To table/column | Cardinality | Active | Cross-filter |
|---:|---|---|---|---|---|
| 1 | `analytics DimDate[FullDate]` | `LocalDateTable_3f018e58…[Date]` | Many-to-one | Yes | Single |
| 2 | `analytics FactTransaction[InvoiceDate]` | `LocalDateTable_6199474d…[Date]` | Many-to-one | Yes | Single |
| 3 | `analytics CustomerRFM[ReferenceDate]` | `LocalDateTable_144d4733…[Date]` | Many-to-one | Yes | Single |
| 4 | `analytics CustomerRFM[FirstPurchaseDate]` | `LocalDateTable_5dc9f7ea…[Date]` | Many-to-one | Yes | Single |
| 5 | `analytics CustomerRFM[LastPurchaseDate]` | `LocalDateTable_16b82e2b…[Date]` | Many-to-one | Yes | Single |
| 6 | `analytics CustomerCohort[FirstPurchaseDate]` | `LocalDateTable_d8aa6b57…[Date]` | Many-to-one | Yes | Single |
| 7 | `analytics CustomerRepeatBehavior[FirstPurchaseDate]` | `LocalDateTable_221a641f…[Date]` | Many-to-one | Yes | Single |
| 8 | `analytics CustomerRepeatBehavior[SecondPurchaseDate]` | `LocalDateTable_f80d9302…[Date]` | Many-to-one | Yes | Single |
| 9 | `analytics FactTransaction[DateKey]` | `analytics DimDate[DateKey]` | Many-to-one | Yes | Single |
| 10 | `analytics FactTransaction[CustomerKey]` | `analytics DimCustomer[CustomerKey]` | Many-to-one | Yes | Single |
| 11 | `analytics FactTransaction[ProductKey]` | `analytics DimProduct[ProductKey]` | Many-to-one | Yes | Single |
| 12 | `analytics FactTransaction[CountryKey]` | `analytics DimCountry[CountryKey]` | Many-to-one | Yes | Single |
| 13 | `analytics CustomerRFM[CustomerKey]` | `analytics DimCustomer[CustomerKey]` | One-to-one | Yes | Both directions |
| 14 | `analytics CustomerCohort[CustomerKey]` | `analytics DimCustomer[CustomerKey]` | One-to-one | Yes | Both directions |
| 15 | `analytics CustomerRepeatBehavior[CustomerKey]` | `analytics DimCustomer[CustomerKey]` | One-to-one | Yes | Both directions |

There are no inactive relationships and no many-to-many relationships. `analytics CohortRetention` and `analytics CohortRevenue` are disconnected and have no relationship to each other or to customer/date tables.

## Date-model findings

- `DimDate[FullDate]` is `dateTime` with `UnderlyingDateTimeDataType = Date`; `DateKey` is `int64`.
- Year, Quarter, MonthNumber, MonthName, YearMonth, WeekOfYear, DayOfMonth, DayName, and DayOfWeekNumber are present.
- The Import partition reads the complete SQL `analytics.DimDate`; the governed SQL documentation records its range as 2009-12-01 through 2011-12-09.
- `MonthName` has no `sortByColumn` assignment to `MonthNumber`, so alphabetical month sorting is a current usability risk.
- `YearMonth` already exists as string and does not need to be recreated.
- The model has `__PBI_TimeIntelligenceEnabled = 1`, one hidden template, eight hidden LocalDateTable objects, and eight automatic date relationships.
- `DimDate` is not explicitly marked as the model date table in the inspected TMDL.

## Customer analytics findings

CustomerRFM, CustomerCohort, and CustomerRepeatBehavior retain the intended one-row-per-eligible-customer grain and use `int64 CustomerKey`, matching DimCustomer. Their one-to-one relationships do not multiply rows at the current validated SQL grain.

All three relationships use bidirectional filtering. This allows a filter from any customer analytical table to propagate through DimCustomer into FactTransaction and the other customer analytical tables. No duplicate relationship path exists today, but the setting creates unnecessary coupling and makes future ambiguity easier to introduce. The safer future design is single-direction filtering from DimCustomer to each customer analytical table.

## Cohort summary findings

CohortRetention and CohortRevenue both retain the expected AcquisitionCohort × CohortIndex grain. They are currently disconnected, which avoids customer-row multiplication and accidental summary-fact joins. This is safe as a baseline. Future measures can use their own cohort/index columns or a deliberately designed shared cohort axis; the tables should not be directly related to each other merely because their grains match.

## Model risks and later column hygiene

### REVIEW findings

- Eight LocalDateTable objects plus the template duplicate calendar logic already available in DimDate and add hidden model complexity.
- Three bidirectional customer relationships permit unintended filter propagation and could create ambiguous paths as the model grows.
- `RetentionRate`, `RevenuePerOriginalCustomer`, `OrdersPerOriginalCustomer`, and repeated `CohortSize` columns default to Sum, which can produce misleading totals without governed measures.
- No measures exist, so report authors can currently rely only on implicit aggregation of raw columns.
- `MonthName` is not sorted by MonthNumber, and DimDate is not explicitly marked as a date table.
- Every imported business column is visible, including surrogate keys, technical lineage, data-quality fields, duplicate flags, and helper columns.
- The local `localhost` connection is environment-specific and will require an explicit deployment/gateway strategy later.
- PBIP `.pbi` local settings and `cache.abf` are local artifacts and should not be included in a future source-control commit.

### Candidate columns to hide later

- All surrogate keys shown to report users: DateKey, CustomerKey, ProductKey, CountryKey, and TransactionLineKey.
- Fact lineage/technical fields: SourceSheet, SourceRowNumber, DQReviewReason, ExactDuplicateGroupSize, and duplicate flags unless used on a dedicated data-quality page.
- Repeated CustomerID and FirstPurchaseDate fields in customer analytical tables when the conformed DimCustomer/customer view is used.
- RFM helper fields such as RFM_Total or RFM_Code if they are not part of the report experience.
- ObservationStatus and boundary/partial flags from general user browsing while retaining them for governed measures and caveat logic.

## Recommended next semantic-model changes

1. Mark DimDate as the date table, configure MonthName sorting, and disable Auto Date/Time so the eight LocalDateTable objects can be removed deliberately.
2. Change the three customer analytical relationships to single-direction DimCustomer filtering after confirming intended report interactions.
3. Keep CohortRetention and CohortRevenue disconnected pending a deliberate cohort-axis design.
4. Add governed explicit measures and formats before building visuals; avoid implicit sums of rates and per-customer metrics.
5. Hide technical fields and organize user-facing columns without changing SQL definitions.
6. Preserve the one-page, zero-visual report baseline until semantic-model validation is complete.

