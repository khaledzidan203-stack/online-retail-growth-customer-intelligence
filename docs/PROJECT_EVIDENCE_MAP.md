# Project Evidence Map

| Claim | Primary evidence | Evidence type |
|---|---|---|
| 1,044,848 canonical rows | management validation JSON + validation docs | Retained analytical evidence |
| Sales Revenue 19,701,685.507 | management validation JSON | SQL/reference reconciliation evidence |
| 11,221,960 units | management validation JSON | SQL/reference reconciliation evidence |
| 39,519 orders | management validation JSON | SQL/reference reconciliation evidence |
| 5,852 sales customers | management validation JSON | SQL/reference reconciliation evidence |
| 4,234 repeat / 1,618 one-time | SQL/Python customer analytics + README/validation docs | Retained analytical evidence |
| Cancellation Value 719,692.94 | management validation JSON | SQL/reference reconciliation evidence |
| Cancellation Value Rate 3.5242% | management validation JSON | SQL/reference reconciliation evidence |
| Anonymous Sales Revenue 2,576,013.46 | management validation JSON | SQL/reference reconciliation evidence |
| 10 report pages | PBIR page definitions + CI | Committed source + automated structural check |
| 136 visuals | PBIR visual definitions + CI | Committed source + automated structural check |
| 50 explicit measures | `_Measures.tmdl` + CI | Committed semantic source + automated check |
| 7 active relationships | `relationships.tmdl` + CI | Committed semantic source + automated check |
| 15 TMDL files | semantic-model source + CI | Committed source + automated check |
| 10 authentic screenshots | `screenshots/` + CI | Retained runtime/presentation evidence |
| 14-sheet management workbook | workbook + validation JSON + CI package check | Retained deliverable |
| 16-sheet detail workbook | workbook + validation JSON + CI package check | Retained deliverable |
| 82,847 validated management cells | validation JSON | Retained workbook reconciliation evidence |
| 433,816 validated detail cells | validation JSON | Retained workbook reconciliation evidence |
| Fresh SQL Server execution in GitHub Actions | no SQL Server job | **Not claimed** |
| Fresh Power BI Desktop runtime in GitHub Actions | no Desktop runtime | **Not claimed** |
| Profit / COGS / ROI / inventory valuation | unsupported by source | **Not claimed** |

## Evidence rule

Current GitHub CI validates the integrity and internal consistency of committed artifacts.

Historical SQL, Power BI Desktop, and workbook reconciliation evidence remains clearly separated from fresh CI execution.
