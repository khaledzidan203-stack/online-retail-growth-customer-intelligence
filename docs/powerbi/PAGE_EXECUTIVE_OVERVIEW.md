# Power BI Report Page 02 — Executive Overview

## Purpose

`Executive Overview` provides a compact leadership view of sales, orders, customers, cancellation exposure, monthly performance, RFM segment value, and the leading markets and products. It uses only governed semantic-model fields and existing explicit measures.

## Page Structure

The page uses the existing 1920 × 1080 canvas and the Power BI base theme with no custom theme, decorative background, or branding treatment.

| Area | Content |
|---|---|
| Header | Page title, native `HOME` page-navigation button, Year slicer, Country slicer |
| KPI row | Sales Revenue, Orders, Sales Customers, Average Order Value, Cancellation Value Rate |
| Middle | Monthly Sales Trend at approximately two-thirds width; Revenue by Customer Segment at approximately one-third width |
| Bottom | Top Markets by Sales Revenue and Top Products by Sales Revenue at equal widths |
| Footer | Partial-period interpretation note for 2009 and 2011 |

## Navigation

The page contains one native `actionButton` labeled `HOME`. Its action is enabled, its type is `PageNavigation`, and its destination is the existing `INDEX` page identifier. No bookmark or text-box navigation is used.

## Slicers

| Slicer | Binding | Mode |
|---|---|---|
| Year | `analytics DimDate[Year]` | Native dropdown slicer |
| Country | `analytics DimCountry[Country]` | Native dropdown slicer |

Both slicers filter fact-based KPIs and charts through the existing single-direction semantic relationships.

Each slicer shows one centered visual title and its dropdown control. The native slicer header/field label is disabled, preventing the bound field name from appearing a second time. Subtitles are disabled and zero container padding preserves the usable dropdown area within the existing dimensions.

## KPI Cards

Five equal-size native card visuals use the existing measures below:

1. `[_Measures].[Sales Revenue]`
2. `[_Measures].[Orders]`
3. `[_Measures].[Sales Customers]`
4. `[_Measures].[Average Order Value]`
5. `[_Measures].[Cancellation Value Rate]`

No new measure, calculated column, calculated table, relationship, or SQL object was introduced.

Each card shows one centered visual title and the KPI callout value only. The card category label and subtitle are disabled, so the measure name is not repeated below the title. Existing measure bindings and model formats are preserved.

## Analytical Visuals

| Visual | Type | Category | Value | Sort / filter | Additional tooltips |
|---|---|---|---|---|---|
| Monthly Sales Trend | Native line chart | `analytics DimDate[YearMonth]` | `[Sales Revenue]` | YearMonth ascending | Orders, Sales Customers |
| Revenue by Customer Segment | Native clustered horizontal bar chart | `analytics CustomerRFM[Segment]` | `[Segment Revenue]` | Segment Revenue descending; all nine governed segments | Segment Customers, Segment Revenue Share |
| Top Markets by Sales Revenue | Native clustered horizontal bar chart | `analytics DimCountry[Country]` | `[Sales Revenue]` | Visual Top 5; Sales Revenue descending | Orders, Sales Customers, Average Order Value |
| Top Products by Sales Revenue | Native clustered horizontal bar chart | `analytics DimProduct[RepresentativeDescription]` | `[Sales Revenue]` | Visual Top 5; Sales Revenue descending | Units Sold, Orders |

The line chart has data labels, legend, and markers disabled. The three bar charts have data labels enabled and legends disabled; axis titles are disabled. Native tooltips remain available.

Every analytical chart has exactly one centered, business-readable title. Visual subtitles are explicitly disabled, including Power BI's auto-generated field descriptions such as measure-and-column summaries.

## Report-Wide Visual Title Standard

Future report pages must follow this standard:

1. Show one visible title per visual.
2. Center visual titles.
3. Use business-readable wording.
4. Keep subtitles off by default.
5. Use a subtitle only when it adds essential business context not already clear from the title.
6. Show `Title + Value` only on KPI cards unless additional context is explicitly required.
7. Show one title and the interactive control on slicers; disable the slicer header when it would repeat the field name.
8. Never expose auto-generated technical descriptions such as `Measure A, Measure B by Column X` as visible subtitles.

## Interaction Exception

`analytics CustomerRFM` is a governed customer-summary snapshot rather than a fact table connected to `analytics DimDate` or `analytics DimCountry`. To avoid suggesting unsupported cross-domain filtering, the Year and Country slicer interactions with `Revenue by Customer Segment` are explicitly set to `NoFilter`. No relationship or forced filter path was added. The slicers continue to filter the fact-based KPI, monthly, market, and product visuals through valid model paths.

## Boundary Note

The page footer states:

> 2009 and 2011 contain partial observation periods; year comparisons should be interpreted accordingly.

## Validation

| Check | Result |
|---|---:|
| Executive Overview visuals | 14 |
| Native Home buttons | 1 |
| Native slicers | 2 |
| Native KPI cards | 5 |
| Native analytical charts | 4 |
| Text boxes | 2 |
| Visual Top 5 filters | 2, both set to 5 |
| Duplicate slicer labels | 0 |
| Duplicate KPI labels | 0 |
| Analytical chart titles | 4, centered |
| Visible analytical chart subtitles | 0 |
| Invalid JSON | 0 |
| Broken semantic bindings | 0 |
| Navigation errors | 0 |
| Visuals outside canvas | 0 |
| PBIR schema validation | PASS — 38 files, 0 errors |
| Semantic measures | Unchanged at 50 |
| Semantic relationships | Unchanged at 7 |
| Other analytical pages modified | 0 |
