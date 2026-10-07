# Final Release Validation

## Release scope

This hardening release improves repository governance, documentation, regression coverage, CI visibility, and presentation neutrality while preserving the validated analytical core.

## Fresh GitHub CI validates

- required project artifacts;
- retained validation JSON status and reference values;
- Power BI page count;
- Power BI visual count;
- explicit DAX measure count;
- active relationship count;
- TMDL file count;
- screenshot count;
- PBIR JSON syntax;
- management-workbook ZIP structure;
- expected workbook sheet counts;
- protected-core Git blob hashes;
- raw/local data exclusions;
- presentation and evidence boundaries;
- common secret/private-key/network patterns.

## Retained historical analytical evidence

Existing validation records support:

- SQL validation PASS;
- reference reconciliation PASS;
- final 10-page Power BI report status;
- 136 report visuals;
- 50 DAX measures;
- 7 active relationships;
- 15 TMDL files;
- 14-sheet management workbook;
- 16-sheet analytical-detail workbook;
- validated Excel-cell totals.

## Runtime boundaries

- Python pipeline source: implemented.
- SQL Server pipeline source: implemented.
- Power BI PBIP/PBIR/TMDL source: implemented.
- Authentic Power BI screenshots: retained.
- Excel management workbooks: retained.
- Fresh SQL Server runtime in CI: not claimed.
- Fresh Power BI Desktop refresh in CI: not claimed.
- Raw UCI workbook: intentionally excluded.
- Canonical local Parquet: intentionally excluded.

## Protected core

The validation script pins selected analytical artifacts by Git blob SHA so presentation/documentation changes cannot silently alter validated source, model, workbook, or screenshot evidence.

Changing a protected analytical artifact requires explicit review and an intentional validator update.
