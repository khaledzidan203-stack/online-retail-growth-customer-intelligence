# Security & Data Publication Policy

## Public repository scope

This repository may contain:

- source code;
- SQL definitions;
- Power BI source files;
- documentation;
- authentic report screenshots;
- validated management workbooks;
- retained analytical reconciliation evidence;
- public dataset acquisition instructions.

Do not commit:

- credentials, passwords, tokens, API keys, private keys, or certificates;
- private database connection strings;
- internal server names or private network addresses;
- machine-local Power BI caches;
- SQL Server MDF/LDF/backup files;
- the raw UCI workbook when local-only publication policy requires exclusion;
- local canonical Parquet extracts;
- unrelated personal or confidential data.

## Analytical integrity

Security also includes integrity of analytical evidence.

Do not silently:

- change transaction classification precedence;
- alter governed KPI definitions;
- overwrite validated management workbooks;
- modify PBIP/PBIR/TMDL source while continuing to cite old QA evidence;
- replace authentic report captures with reconstructed images;
- change retained reconciliation JSON without rerunning the appropriate analytical validation.

Selected validated artifacts are pinned by Git blob SHA in the repository validator.

## Reporting a problem

If a secret or sensitive artifact is discovered, remove it from the affected branch/history as appropriate and rotate any exposed credential outside this repository. Do not post the sensitive value in a public issue.
