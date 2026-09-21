# Master Report Design Audit

## Scope and evidence

This is a read-only reverse-engineering audit of the existing PBIP/PBIR implementation under `powerbi/`. Pages were located from `page.json.displayName`, not assumed IDs.

| Completed page | Discovered page ID | Visuals |
|---|---|---:|
| Executive Overview | `74096d393d05fa994d48` | 14 |
| Sales Performance | `a369ddaae564507e3f13` | 15 |
| Customer Intelligence | `3a0bc45db57e44eabc9f` | 15 |
| RFM Segmentation | `3dc34e438964572c23de` | 12 |
| Cohort & Retention | `cb83fd6093f4e60d08b4` | 12 |
| Product Performance | `94ed48295c46b4214aa5` | 14 |

All 82 visual definitions on these pages were parsed and inventoried. The audit also covered report `pages.json`, all six `page.json` files, relationships, `_Measures.tmdl`, and relevant fact/dimension/summary TMDL.

## 1. Master Design System

### Page shell

- Canvas: `1920 x 1080`; `displayOption=FitToPage`.
- Page background and outspace: literal `#0B1220`, transparency `0D`.
- Standard content margin: 60 px; working width: 1,800 px.
- Standard title geometry: `560,18,800,82`.
- Standard HOME geometry: `1690,20,170,50` (Executive uses `1680,30,180,55`).
- Page titles use transparent native `basicShape`, not textbox: rounded-rectangle shape, VCO title/subtitle, fill off, line transparency 100D, background/header/border off.
- No completed page uses a fake full-page background visual.

### Verified tokens

| Role | Exact value |
|---|---|
| Page and slicer background | `#0B1220` |
| KPI fill | `#303030` |
| Primary text | `#F8FAFC` |
| Secondary text | `#CBD5E1` |
| Muted/helper text | `#94A3B8` |
| Primary analytical accent | `#20C7B7` |
| Warning accent | `#F5B942` |
| Negative/risk | `#E45B64` |
| Legacy table negative | `#D64554` |
| Gridlines | `#334155` |
| Border/outline | `#64748B` |
| HOME outline | `#5EEAD4` |

Font is Segoe UI. Page title is 24D bold, subtitle 11D, chart/KPI titles usually 14D bold, KPI values 24D bold, table headers 12D bold, table values 11D, and footnotes 10D.

KPI cards use `objects.fillCustom=#303030`. Charts use transparent backgrounds and a VCO border (`#64748B`, radius 8D, width 1D). Typical chart padding is 8D top/bottom and 16D left/right. Shadows are off.

## 2. Common Page Grammar

`Header -> optional slicers -> KPI row -> analytical area -> optional footnote`

| Page | Actual implementation |
|---|---|
| Executive Overview | Year/Country y=105; 5 KPIs y=195; trend/drivers y=330; market/product drivers y=650; footnote y=970. |
| Sales Performance | Year/Month/Country y=85; 6 KPIs y=175; trend y=300; combo/column analysis near y=549; footnote y=1020. |
| Customer Intelligence | Year/Country y=90; 6 KPIs y=180; composition y=310; detail y=510; ranking y=765; footnote y=1020. |
| RFM Segmentation | Segment y=85; 5 KPIs y=165; segment bars y=305; scorecard y=555; Top 10 y=805; no footnote. |
| Cohort & Retention | No slicers; 5 milestone KPIs y=135; 2x2 analysis grid y=260/585; footnote y=965. |
| Product Performance | Year/Country y=105; 5 KPIs y=195; value/volume y=330; risk/detail y=650; footnote y=970. |

## 3. Exact donor map

| Component | Donor page / visual folder | Type, geometry, and use |
|---|---|---|
| Title/subtitle | Product / `pp00000000000000001` | `basicShape`, 560,18,800,82; 24D white title and 11D muted subtitle. |
| HOME | Product / `pp00000000000000002` | `actionButton`, 1690,20,170,50; native PageNavigation to INDEX; rounded 10D, teal fill, mint outline. |
| Year slicer | Product / `pp00000000000000003` | `slicer`, 60,105,260,70; `DimDate[Year]`. |
| Country slicer | Product / `pp00000000000000004` | `slicer`, 340,105,360,70; `DimCountry[Country]`. |
| Month slicer | Sales / `f0000000000000000004` | `slicer`, 280,85,200,70; `DimDate[MonthName]`. |
| Standard KPI | Product / `pp00000000000000005` | `cardVisual`, 60,195,344,110; white value, dark fill. |
| Warning KPI | Product / `pp00000000000000009` | `cardVisual`, 1516,195,344,110; amber value. |
| Market bar | Executive / `e0000000000000000012` | `clusteredBarChart`, 60,650,890,300; Country + Sales Revenue; explicit Top 5. |
| Primary bar styling | Product / `pp00000000000000010` | `clusteredBarChart`, 60,330,890,300; teal ranking grammar. Styling donor only: no explicit TopN filter. |
| TopN + not blank | Customer / `c0000000000000000014` | `clusteredBarChart`, 60,765,1800,245; valid Top 10 and not-blank filters. |
| Risk bar | Product / `pp00000000000000012` | `clusteredBarChart`, 60,650,890,300; risk red. |
| Line trend | Executive / `e0000000000000000010` | `lineChart`, 60,330,1180,300; YearMonth + Sales Revenue. |
| Column | Cohort / `ch00000000000000009` | `clusteredColumnChart`, 1080,260,780,300; labels on, teal, valid Advanced filter. |
| Combo | Sales / `f0000000000000000013` | `lineClusteredColumnComboChart`, 59.30,549.42,1070.93,450; Orders + AOV. |
| Scorecard table | RFM / `r0000000000000000011` | `tableEx`, 60,555,1800,240; 8 values, 2 data bars, 3 icon rules. |
| Ranked table | RFM / `r0000000000000000012` | `tableEx`, 60,805,1800,270; 5 values, TopN=10, descending Monetary. |
| Simple table | Customer / `c0000000000000000013` | `tableEx`, 60,510,1800,250; not-blank filter and descending AOV. Avoid stale icon entries. |
| Footnote | Product / `pp00000000000000014` | `basicShape`, 60,970,1800,45; left-aligned 10D muted text. |

## 4. Slicer donor

Use Product `pp...003/004` and Sales `f...004`.

- Query: one active Column under `queryState.Values.projections`.
- `objects.data.mode='Dropdown'`; native header off.
- `general.outlineColor=#64748B`, weight 1D.
- Items: Segoe UI 11D, `#F8FAFC`, padding 7D, background `#0B1220`.
- VCO title: left, 10D bold white, wrap on.
- Background off/transparency 100D; visual header off; all VCO padding zero.
- Preserve the observed theme-based `dropdown.accentBarColor`; do not invent dropdown properties.

## 5. KPI donors

Use Product `pp...005` for normal and `pp...009` for warning.

- One governed measure in `queryState.Data`.
- Value: centered Segoe UI 24D bold; white normally, `#F5B942` for warning.
- Label off; `fillCustom=#303030`, transparency 0D, default selector.
- Title: centered 14D bold white; subtitle/background/header off.
- Measure format strings control currency/count/percent. Do not add local precision or display-unit properties.

## 6. Horizontal bar donor

For Market Analysis, use Executive `e...012`: Category=Country, Y=Sales Revenue, tooltips Orders/Sales Customers/AOV, descending value sort, VisualTopN=5.

Formatting: labels on white; legend off; category width 10D and inner padding 10D; category text `#CBD5E1`; value text `#94A3B8`; grid `#334155`; teal fill; centered 14D title; transparent background; border `#64748B`, radius 8D, width 1D; padding 8/8/16/16.

For a genuine Top N claim, copy the exact `VisualTopN` structure from `e...012` or `c...014`. Product Top 10 bars have titles but no explicit TopN filter.

## 7. Line, column, and combo donors

- Line: Executive `e...010`. Category YearMonth, Y Sales Revenue, tooltips Orders/Customers, ascending sort, teal series, labels/legend/markers off.
- Column: Cohort `ch...009`. Category AcquisitionCohort, Y Cohort Size, labels on, teal, ascending sort, known-valid left-boundary Advanced filter.
- Combo: Sales `f...013`. Category YearMonth, Y Orders, Y2 AOV; teal columns, amber line, secondary axis and legend on, markers off. Its fractional Desktop geometry should not be propagated to a new page.

All three use white titles, muted axes, subtle gridlines, transparent backgrounds, and the rounded 8D border pattern.

## 8. Table donors

Safest full donors are RFM `r...011` and `r...012`.

- RFM scorecard: 6D row padding, 12D bold headers, 11D values, auto-size on, word-wrap off, totals off; two teal data bars with visible values and three icon rules.
- RFM Top 10: 3D row padding, same typography, totals off; explicit TopN=10 and Monetary descending; one data bar and icon rules.
- Customer `c...013` demonstrates a valid not-blank filter and simple four-column Values query, but includes stale RFM icon-formatting entries not represented in its query. Reuse only its clean query/filter and base table styling.
- Product `pp...013` is not a safe full donor in its current serialized state; see structural findings.
- Table binding role is `queryState.Values`. Conditional rules use wildcard selectors plus exact metadata. Data bars live under `objects.columnFormatting`; keep numeric text visible with `hideText=false`.

## 9. Footnote donor

Product `pp...014` is canonical: transparent rounded `basicShape`, 60,970,1800,45; VCO title used as the note, left aligned, Segoe UI 10D, normal weight, `#94A3B8`; subtitle/background/header/border off.

## 10. Navigation donor

Product `pp...002` is canonical:

- `actionButton` with blank/hidden icon and visible HOME text.
- `visualContainerObjects.visualLink`: show=true, type=`PageNavigation`, destination page ID `3fd4c3006aab15189332` (INDEX).
- RoundedByPixel 10D, teal fill `#20C7B7`, mint outline `#5EEAD4`, dark text `#0B1220`.
- Current report audit: 15 page-navigation links, 0 invalid destinations.

## 11. Current semantic model capabilities

### Topology and grains

The model has 10 visible SQL-backed business tables plus relationship-free `_Measures`. It contains 50 explicit measures and seven active M:1 single-direction relationships:

| Many side | One side |
|---|---|
| FactTransaction[DateKey] | DimDate[DateKey] |
| FactTransaction[CustomerKey] | DimCustomer[CustomerKey] |
| FactTransaction[ProductKey] | DimProduct[ProductKey] |
| FactTransaction[CountryKey] | DimCountry[CountryKey] |
| CustomerRFM[CustomerKey] | DimCustomer[CustomerKey] |
| CustomerCohort[CustomerKey] | DimCustomer[CustomerKey] |
| CustomerRepeatBehavior[CustomerKey] | DimCustomer[CustomerKey] |

`CohortRetention` and `CohortRevenue` are disconnected by design. FactTransaction is transaction-line grain; dimensions are one row per date/customer/product/country; CustomerRFM, CustomerCohort, and CustomerRepeatBehavior are one row per customer; cohort facts are AcquisitionCohort x CohortIndex.

### Available fields

- Geography: `DimCountry[Country]`; technical CountryKey is hidden.
- Time: FullDate, Year, Quarter, MonthName (sorted by hidden MonthNumber), YearMonth, WeekOfYear, DayOfMonth, DayName.
- Customer: `DimCustomer[CustomerID]`.
- Product: StockCode, RepresentativeDescription, ItemClass.
- Fact detail: Invoice, InvoiceDate, LineDescription, Quantity, Price, LineAmount, ItemClass, TransactionClass. Governance flags are hidden.
- RFM: ReferenceDate, Recency, Frequency, Monetary, R/F/M scores, RFM_Code, Segment, first/last purchase dates, units, lifespan, AOV.
- Cohort: AcquisitionCohort, CohortIndex, ActivityMonth and governed retention/revenue/order measures.

### Governed measures relevant to future pages

- Core sales: Sales Revenue, Average Order Value.
- Orders/units: Orders, Units Sold, Average Units per Order.
- Customers: Sales Customers, Known Customer Revenue, Revenue per Known Customer, Orders per Known Customer, Repeat Customers, One-Time Customers, Repeat Customer Rate.
- Cancellation: Cancellation Value, Cancellation Units, Cancellation Invoices, Customers with Cancellations, Cancellation Value Rate.
- Time: Sales Revenue PY/YoY/YoY %, Orders PY/YoY %, Units Sold PY/YoY %, Sales Revenue YTD/MTD.
- Market analysis: no dedicated market-count measure exists. Use `DimCountry[Country]` with fact-based measures above.
- Known/anonymous: Known Customer Revenue, Anonymous Sales Revenue, Anonymous Sales Revenue %.
- Quality: Canonical Transaction Rows, Sales Eligible Rows, Duplicate Flagged Revenue, Duplicate Revenue Impact %, Operational Adjustment Rows, DQ Review Rows.
- Specialized: nine RFM measures and seven cohort/retention measures are available but should not be presented as country-filterable without a valid model path.

Auto Date/Time is disabled; DimDate is the sole governed date table. Summary-table numeric columns generally use summarizeBy none; additive fact fields retain Sum.

## 12. PBIR safety checklist

- Read the complete current file before any edit.
- Close Power BI Desktop before creating, deleting, or renaming visuals.
- Use only properties and selectors observed in a current working donor.
- Folder ID must equal internal `name`.
- Preserve UTF-8 without BOM.
- Parse JSON before writing and after every edit.
- Preserve query, sort, filter, and interaction structures unless analytical logic is explicitly authorized.
- Copy a complete donor structure; avoid broad string replacements.
- Use page-level background/outspace, never a full-canvas background visual.
- Do not introduce `stylePreset` or custom `visualTooltip`; neither occurs in the current 93 visual files.
- Revalidate: invalid JSON, duplicate IDs, folder/name mismatch, outside-canvas visuals, bindings, navigation.
- Current read-only baseline: Invalid JSON=0; duplicate IDs=0; folder/name mismatch=0; outside canvas=0; broken queryRefs=0; navigation errors=0.

### Structural findings and donor cautions

1. Product `pp00000000000000013`: `objects.columnFormatting` is an object containing an embedded duplicate visual definition instead of the expected array. JSON parses, but the serialized shape is inconsistent and must not be copied wholesale.
2. Customer `c0000000000000000013`: base table/query/filter are usable, but the visual retains RFM icon rules for fields not projected by the table.
3. RFM `r0000000000000000012`: one Monetary-related icon rule references `_Measures[Average RFM Monetary]` while the query projects the raw `CustomerRFM[Monetary]` column. Preserve the currently working visual, but do not generalize this selector.
4. Product bars `pp...010-012`: titles claim Top 10 but the files contain no explicit VisualTopN filter. Use their formatting, not their ranking contract.
5. Sales lower visuals use fractional geometry, and the RFM title geometry deviates from the standard 560/18/800/82 header. These are alignment inconsistencies, not JSON errors.

## 13. Recommended construction strategy for Market Analysis

Do not build yet. The blank page already exists as `a66fffbd25453738ce11`.

### Questions the page should answer

1. Which countries contribute the most sales revenue?
2. How do market rankings differ for orders, units, customers, and AOV?
3. Which markets have elevated cancellation value or cancellation rate?
4. How has revenue changed over time for a selected market?
5. How concentrated is revenue across the leading markets?
6. How much revenue is known-customer versus anonymous by market?

### Available data

Use `DimCountry[Country]`, `DimDate[Year]`, `MonthName`, and `YearMonth` with Sales Revenue, Orders, Units Sold, Sales Customers, Average Order Value, Known Customer Revenue, Anonymous Sales Revenue, Anonymous Sales Revenue %, Cancellation Value, Cancellation Units, Cancellation Invoices, Customers with Cancellations, and Cancellation Value Rate.

There is no latitude/longitude, region hierarchy, or validated map donor. Prefer ranked bars and a detail table over inventing a map configuration. Country filters reach FactTransaction through the active single-direction relationship. Do not use RFM or disconnected cohort measures as market-responsive metrics.

### Reuse plan

- Shell/title/subtitle: Product `pp...001`.
- HOME: Product `pp...002`.
- Year and Country slicers: Product `pp...003/004`; add Month only if required using Sales `f...004`.
- KPI row: Product normal/warning cards.
- Revenue trend: Executive line donor `e...010`.
- Market ranking: Executive market donor `e...012`, including its explicit TopN structure.
- Cancellation-risk ranking: Product risk bar styling `pp...012`, but bind Country and a cancellation measure and add an explicit TopN filter.
- Market detail table: start from RFM base table grammar, remove all RFM-specific conditional selectors, and add only validated country and governed-measure projections. Do not use Product `pp...013` until its structure is repaired.
- Footnote: Product `pp...014`, used only for partial-period or metric-definition context.

Suggested composition: header; Year/Country slicers; five KPI cards (Revenue, Orders, Units, Customers, AOV or Cancellation Rate); left revenue trend; right Top Markets; lower cancellation-risk bar plus country detail table; optional footnote. Keep the 60 px margins, 20 px gaps, transparent visual backgrounds, 8D rounded borders, and existing accent semantics.

## Audit conclusion

Completed pages inspected: 6 (82 visuals). Donor visuals selected: 18 role-specific donors, including separate safe donors for explicit TopN, conditional tables, navigation, and footnotes.

Structural inconsistencies were discovered, principally the malformed-type `columnFormatting` payload in Product Performance `pp...013`, plus stale conditional-format selectors and missing explicit TopN filters noted above. No project file was changed by this audit; the only authorized output is this file outside `powerbi/`.
