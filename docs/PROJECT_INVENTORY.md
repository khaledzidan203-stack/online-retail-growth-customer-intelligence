# Project Inventory

| Area | Classification | Treatment |
|---|---|---|
| README, changelog, requirements, gitignore | KEEP | Project guide and repository hygiene |
| sql/ | KEEP | DDL, raw/staging/analytics, business analysis and validation |
| src/ | KEEP | Profiling, cleaning, analytics, SQL publishing and exports |
| powerbi/ | KEEP | Native PBIP, PBIR, TMDL, DAX and report source |
| docs/ | KEEP | Architecture, KPIs, governance, evidence and validation |
| outputs/management/ | KEEP | Two validated Excel deliverables plus reconciliation JSON |
| screenshots/ | KEEP | Ten authentic Power BI report captures |
| config/item_classification.json | KEEP | Governed item-classification reference |
| data/raw/online_retail_II.xlsx | LOCAL ONLY | Official UCI source workbook; intentionally excluded |
| data/interim/canonical_transactions.parquet | LOCAL ONLY | Reproducible local derived dataset; intentionally excluded |
| powerbi/**/.pbi/, *.abf | LOCAL ONLY | Machine-local Power BI state/cache |
| CHECKPOINT_*, BACKUP_*, BROKEN_*, PROJECT_SNAPSHOT_* | LOCAL ONLY | Recovery and audit artifacts excluded from publication |
| Compiled database files / backups | DENY | Not required for public analytical source |
| Secrets / credentials | DENY | Never publish |

## Core publication principle

The repository publishes analytical source and retained validation evidence, not the raw UCI workbook or machine-local runtime state.

Presentation hardening must not silently alter the validated SQL, Python, Power BI, Excel, or screenshot evidence.
