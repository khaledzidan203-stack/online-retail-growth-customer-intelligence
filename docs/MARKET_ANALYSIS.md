# Market Analysis

## 1. Objective

Compare market scale, concentration, non-UK opportunity, customer/order economics and cancellation exposure without changing governed business logic.

## 2. Business questions

Which markets lead revenue; how concentrated is sales; which international markets matter; do leaders have customer depth or high order values; where is material cancellation exposure?

## 3. Dataset scope

See [source profile](project/MARKET_ANALYSIS_PROFILE.md): 43 recorded country labels, 2009-12-01 through 2011-12-09. SQL profiling was completed before this build and was not repeated.

## 4. KPIs

Sales Revenue; Orders; Sales Customers; Average Order Value; Cancellation Value Rate. All use existing governed measure formats.

## 5. Visual inventory

15 native visuals: title/subtitle, HOME, two dropdown slicers, five equal-size KPI cards, three Top 5 horizontal bars, an eight-column market economics table, footnote and explicitly static full-period concentration note.

## 6. Analytical logic

Overall revenue ranking retains the UK. Separate international ranking exposes smaller markets. Economics table shows Country, Sales Revenue, Orders, Sales Customers, Units Sold, Average Order Value, Cancellation Value and Cancellation Value Rate, sorted by Sales Revenue descending. Revenue data bars retain numeric values; totals off. All 43 markets remain available through intentional table scrolling.

## 7. Filters

Year uses analytics DimDate; Country uses analytics DimCountry. Default slicer interactions are enabled for fact-based visuals; no exceptions. Rankings sort descending by the plotted measure. HOME uses native Page Navigation to INDEX (3fd4c3006aab15189332). The full-period context note is explicitly not filter-responsive.

## 8. Non-UK logic

Only visual ma000000000000000011 excludes Country = United Kingdom, using the existing native Advanced/Not/Comparison donor structure. It intersects the Country slicer; selecting only United Kingdom intentionally leaves this visual empty. No global UK exclusion.

## 9. Cancellation risk

Rank by absolute Cancellation Value, not unqualified rates in very small countries. Rate and scale remain available in tooltips/table. Cancellation Value Rate = Cancellation Value / (Sales Revenue + Cancellation Value). No new volume threshold or business definition.

## 10. Donors

Product Performance pp...001-005, 009 and 014: header, HOME, dropdowns, KPI cards, warning card and footnote. Executive Overview e...012: native Top 5 bar. RFM r...011: safe tableEx and revenue data-bar structure, with irrelevant RFM icon bindings removed from the copy. Customer Intelligence c...013: known-valid Advanced filter syntax. Original donor files unchanged; malformed Product table not used.

## 11. PBIR files

Only powerbi/OnlineRetailAnalytics.Report/definition/pages/a66fffbd25453738ce11/page.json and its 15 new visuals/*/visual.json files. Page background copied from approved donor; 1920 x 1080 canvas retained.

## 12. Visual IDs

All IDs have prefix ma followed by 18 decimal digits:

| Suffix | Purpose |
|---|---|
| 001-004 | Title, HOME, Year, Country |
| 005-009 | Five KPIs in the order listed above |
| 010 | Top 5 Markets by Sales Revenue |
| 011 | Top 5 Non-UK Markets by Revenue |
| 012 | Top 5 Markets by Cancellation Value |
| 013 | Market Economics - All Markets |
| 014-015 | Footnote and static context note |

## 13. Measures

_Measures: Sales Revenue, Orders, Sales Customers, Average Order Value, Cancellation Value Rate, Units Sold, Cancellation Value. No new or modified measures.

## 14. Data quality

Known-customer counts omit anonymous identifiers while eligible sales/orders include anonymous business. Market customer counts are not additive. Preserve EIRE, Unspecified and European Community labels. No geographic imputation.

## 15. Caveats

2009 and 2011 are partial periods. Recorded country is not necessarily customer residence. High AOV does not prove broad customer depth. Small-market cancellation rates are volatile. Static concentration note describes the full period, never the current selection.

## 16. Validation

2026-09-21: 15 visuals; invalid JSON 0; UTF-8 BOM 0; duplicate visual IDs 0 across active report; folder/name mismatches 0; broken bindings 0; navigation errors 0; outside-canvas visuals 0; geometric overlaps 0; unexpected stylePreset/custom visualTooltip 0. Top 5 filter/sort consistency and non-UK exclusion checks pass. Page background preserved. Measures 50; relationships 7.

Before/after SHA-256 checks confirm semantic model, other pages and protected snapshot unchanged. One page-specific prebuild backup: CHECKPOINT_MARKET_ANALYSIS_PREBUILD_20260921_040855. No deletions, commits or pushes.

Official exact-version schema validation is BLOCKED, not PASS: copied donor visuals declare visualContainer 2.12.0, whose public schema URL returns 404; Microsoft's public repository currently publishes only through 2.9.0. A 2.9 compatibility attempt rejects the 2.12 schema identifier and newer inherited spacing properties. These donor structures were preserved rather than downgraded speculatively. Page 2.1 schema validation succeeds. No claim of Power BI runtime validation is made.

## 17. Status

Page implementation complete and ready for manual Desktop review; full schema/runtime sign-off pending. Open the project in its existing Desktop version, check all visuals, exact Top 5 membership, Year/Country behavior, UK-only empty international chart, HOME, table readability and title clipping. Capture a screenshot only after confirming successful rendering.

