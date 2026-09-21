# Portfolio packaging inventory

| Area | Classification | Treatment |
|---|---|---|
| README, changelog, requirements, gitignore | KEEP | Portfolio guide and repository hygiene. |
| sql/ | KEEP | DDL, raw/staging/analytics, analysis and validation. |
| src/ingestion, cleaning, analytics, exports | KEEP | Reproducible pipeline and exports. |
| PBIP, Report and SemanticModel | KEEP | Native PBIR, DAX and TMDL source. |
| docs/ | KEEP | Context, data, architecture, KPIs, pages and validation. |
| outputs/management/ | KEEP | Two workbooks and reconciliation JSON. |
| outputs/figures/ and compact validation summaries | KEEP | Analysis charts/evidence, not report screenshots. |
| screenshots/ | KEEP | Ten genuine Power BI report captures, preserved unchanged. |
| data/raw/online_retail_II.xlsx | IGNORE | Preserve locally; 45.6 MB source workbook excluded from Git. |
| data/interim/canonical_transactions.parquet | IGNORE | Preserve local derived extract; exclude from Git. |
| powerbi/**/.pbi/, *.abf | IGNORE | Machine-local settings/model cache, not source. |
| CHECKPOINT_*, BACKUP_*, BROKEN_*, PROJECT_SNAPSHOT_* | IGNORE | Preserve local recovery files; do not publish. |
| Temporary discovery/profile transcripts | IGNORE | Local working files, not portfolio deliverables. |
| Empty .gitkeep files | KEEP | Preserve useful directory structure. |
| Potential deletes | DELETE-SAFE / REVIEW | None authorized or performed. |

Analytical source is preserved unchanged. In the isolated publication copy only, project planning/audit documents are grouped under docs/project/. Local data, caches, backups and transcripts remain excluded. The original local repository and history are preserved.
