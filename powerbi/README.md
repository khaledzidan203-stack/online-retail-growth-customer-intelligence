# Power BI source

Open [OnlineRetailAnalytics.pbip](OnlineRetailAnalytics.pbip) in a compatible Power BI Desktop version.

| Artifact | Purpose |
|---|---|
| [OnlineRetailAnalytics.Report/](OnlineRetailAnalytics.Report/) | Native report definition: PBIR pages, visuals, interactions and navigation |
| [OnlineRetailAnalytics.SemanticModel/](OnlineRetailAnalytics.SemanticModel/) | TMDL tables, relationships, Power Query partitions and DAX |
| [Report guide](../docs/powerbi_report.md) | All ten pages with real screenshots |

The completed model has **50 explicit DAX measures**, **7 active single-direction relationships** and **15 TMDL files**. The report has **10 pages** and **136 visuals**. All measures live in the disconnected `_Measures` table. [Measure dictionary](../docs/powerbi/DAX_MEASURE_DICTIONARY.md) · [Semantic specification](../docs/powerbi/POWER_BI_SEMANTIC_MODEL.md).

## Open and refresh

1. Reproduce the SQL pipeline in the root [run guide](../README.md#reproduce-the-project).
2. Open the PBIP project in Power BI Desktop.
3. The supplied source references SQL Server `localhost`, database `OnlineRetailAnalytics`. Configure data-source permissions using Windows authentication. If your instance differs, configure your own local copy accordingly.
4. Refresh the model, then use INDEX to navigate the report.

Machine-local caches and credentials are excluded, so a fresh clone requires local SQL connectivity and refresh to show interactive data. Real [screenshots](../screenshots/) allow review without a local refresh.

## QA and interpretation

Final project structural QA and semantic QA: **PASS**, as recorded in the [validation overview](../docs/validation.md). Publication preserves the supplied PBIP, PBIR, TMDL and DAX unchanged. Historical checkpoint notes may record intermediate issues later superseded by final QA; this release does not claim a new Desktop runtime test.

RFM is a snapshot. Disconnected cohort result tables have cohort-period grain. Calendar/country slicers should not be interpreted as dynamically recomputing those precomputed results. See the [model documentation](../docs/data_model.md).
