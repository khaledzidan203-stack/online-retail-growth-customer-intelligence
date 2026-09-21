# RFM Segmentation

## Purpose

The RFM Segmentation page presents the governed current-state customer snapshot. It does not recalculate RFM historically.

- Snapshot reference date: **2011-12-10**
- Grain: one eligible known customer per row in `analytics CustomerRFM`
- Customer identifier: `CustomerRFM[CustomerID]`
- Source governance: `analytics.CustomerRFM.CustomerID` is defined `NOT NULL` and unique.

## Navigation and filtering

- The native **HOME** button uses Page Navigation to the `INDEX` page.
- The only slicer is **RFM Segment**, bound to `CustomerRFM[Segment]` in dropdown mode.
- Default visual interactions allow the Segment slicer to filter every KPI and visual on this page.
- Year and Country slicers are intentionally absent because CustomerRFM is a fixed snapshot. Adding them would imply historical or geographic re-segmentation that the model does not provide.

## KPI cards

| Card title | Governed measure |
|---|---|
| RFM Customers | `[Segment Customers]` |
| RFM Revenue | `[Segment Revenue]` |
| Average Recency | `[Average RFM Recency]` |
| Average Frequency | `[Average RFM Frequency]` |
| Average Monetary | `[Average RFM Monetary]` |

The segment-scoped customer and revenue measures are used so the Segment slicer filters all five cards.

## Visuals

### Customers by RFM Segment

- Native horizontal bar chart
- Category: `CustomerRFM[Segment]`
- Value: `[Segment Customers]`
- Sort: customer count descending
- Additional tooltip measures: `[Segment Customer Share]`, `[Segment Revenue]`, and `[Segment Revenue Share]`

### Revenue by RFM Segment

- Native horizontal bar chart
- Category: `CustomerRFM[Segment]`
- Value: `[Segment Revenue]`
- Sort: revenue descending
- Additional tooltip measures: `[Segment Revenue Share]`, `[Segment Customers]`, and `[Segment Customer Share]`

### RFM Segment Performance

Native table sorted descending by `[Segment Revenue]` with:

- `CustomerRFM[Segment]`
- `[Segment Customers]`
- `[Segment Customer Share]`
- `[Segment Revenue]`
- `[Segment Revenue Share]`
- `[Average RFM Recency]`
- `[Average RFM Frequency]`
- `[Average RFM Monetary]`

Native conditional formatting keeps every numeric value visible:

- Customer Share % and Revenue Share % use blue data bars with the formatted percentage values retained.
- Average Recency uses reversed arrows: up/favorable at 90 days or less, right/neutral between 90 and 300 days, and down/unfavorable at 300 days or more.
- Average Frequency uses normal arrows: up/favorable at 5 or more, right/neutral from 2 to under 5, and down/unfavorable below 2.
- Average Monetary uses normal arrows: up/favorable at 2,000 or more, right/neutral from 500 to under 2,000, and down/unfavorable below 500.
- The total row is disabled because it would duplicate the KPI row rather than improve segment interpretation.

### Top Customers by RFM Value

Native table limited to Top 10 customer identifiers and sorted descending by `CustomerRFM[Monetary]` with:

- `CustomerRFM[CustomerID]`
- `CustomerRFM[Segment]`
- `CustomerRFM[Recency]`
- `CustomerRFM[Frequency]`
- `CustomerRFM[Monetary]`

`CustomerKey` is not exposed. A separate blank filter is unnecessary because the governed source column is non-null.

Monetary uses a blue data bar with the value retained. Frequency uses normal arrows (favorable at 100 or more; unfavorable below 50), while Recency uses reversed arrows (favorable at 5 days or less; unfavorable at 15 days or more). Intermediate values use a neutral right arrow. The total row is disabled.

## Presentation standard

All visual titles are centered and bold, subtitles are disabled, backgrounds are transparent, single-series legends are hidden, bar data labels are enabled, and card category labels are disabled. Table columns auto-size, use compact row padding, retain visible numeric values, and avoid unnecessary totals.
