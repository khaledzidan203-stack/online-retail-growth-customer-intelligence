# Presentation Assets

This repository uses **authentic Power BI report captures** as presentation evidence.

The primary README visual is:

`screenshots/02_executive_overview.png`

## Evidence-supported scope

The repository contains:

- a native Power BI PBIP project;
- PBIR report definitions;
- TMDL semantic-model source;
- 10 report pages;
- 136 report visuals;
- 50 explicit DAX measures;
- 7 active single-direction relationships;
- 15 TMDL files;
- 10 genuine report screenshots;
- SQL Server raw, staging, dimensional, analytical, customer, and validation layers;
- Python profiling, cleaning, analytics, RFM, cohort, SQL publishing, and Excel export code;
- two validated management workbooks;
- retained reconciliation evidence in `outputs/management/management_export_validation.json`.

## Evidence boundary

The screenshots are **runtime presentation evidence from the completed report**, not synthetic mockups.

Publication preserves the existing report screenshots and validated analytical artifacts. Current GitHub Actions validation does not launch Power BI Desktop, provision SQL Server, or rerun the full external-source pipeline.

Therefore:

- PBIP / PBIR / TMDL source = implemented source artifact;
- screenshots = retained report-runtime evidence;
- management workbooks = retained validated deliverables;
- SQL/Python runtime baselines = retained historical analytical evidence;
- fresh GitHub CI = structural, evidence, privacy, and regression validation of committed artifacts.

No additional hero image should invent KPIs, product names, market results, or report states beyond the retained evidence.
