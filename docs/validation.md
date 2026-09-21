# Validation

## Final project and publication scope

The supplied final report QA records structural PASS and semantic PASS: 10 pages, 136 visuals, 50 measures, seven relationships and 15 TMDL files. Earlier checkpoint documents record intermediate model/page states and should be read as history.

The isolated publication package was checked independently for valid JSON, the same artifact counts, unchanged analytical source/workbook/screenshot bytes, ten real screenshots, working relative documentation links, raw-data/cache exclusions, private identifiers and file sizes below 100 MB. Gitleaks found no leaks. Both README Mermaid diagrams were rendered successfully with Mermaid CLI and a local browser.

Publication checks do not rerun SQL analytics, Excel generation, Power BI Desktop refresh or runtime visual tests. The existing project validation and Excel reconciliation records provide that prior analytical evidence. No analytical definitions or values were changed for publication.

Checkpoint-specific SQL, Python, Power BI and semantic evidence is under [docs/validation](validation/). Final report QA records 10 pages, 136 visuals, 50 measures, 7 relationships, 15 TMDL files, zero invalid page/visual JSON, zero global ID duplication, zero off-canvas visuals, zero navigation issues and zero semantic content issues.

Reproduce workbook generation and validation:

~~~powershell
python src/exports/management_export.py
python src/exports/management_export.py --validate-only
~~~

The export recomputes fact-level SQL baselines, checks reference values, reconciles view rollups and checks saved analytical cells against fresh SQL results. Evidence: outputs/management/management_export_validation.json. Confirmed: management workbook 14 sheets, detail workbook 16 sheets, SQL and reference reconciliation PASS.

References: 19,701,685.507 revenue; 11,221,960 units; 39,519 orders; 5,852 sales customers; 719,692.94 cancellation value; 3.5242% cancellation rate; 2,576,013.46 anonymous sales; 3,392 operational-adjustment rows; 1,044,848 canonical rows.
