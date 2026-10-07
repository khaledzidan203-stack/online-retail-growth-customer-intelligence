# Validation

## Current evidence model

The repository separates **fresh GitHub CI** from **historical / retained analytical runtime evidence**.

### Fresh GitHub CI

The current workflow validates committed artifacts without provisioning SQL Server, downloading the raw UCI workbook, or launching Power BI Desktop.

It checks:

- protected analytical-core Git blob hashes;
- management-validation JSON baselines;
- workbook ZIP/package structure and expected sheet counts;
- PBIR JSON validity;
- 10 report pages;
- 136 visuals;
- 50 explicit DAX measures;
- 7 relationships;
- 15 TMDL files;
- 10 authentic report screenshots;
- raw/local-data exclusions;
- publication boundary and public-text safety;
- committed artifact regression tests.

### Historical / retained analytical evidence

The completed project retains prior analytical validation supporting:

- SQL validation PASS;
- reference reconciliation PASS;
- Power BI structural QA PASS;
- Power BI semantic QA PASS;
- Excel saved-cell reconciliation PASS;
- authentic report captures.

The existing completed-report baseline is:

- 10 pages
- 136 visuals
- 50 explicit measures
- 7 relationships
- 15 TMDL files

The retained management validation record confirms:

- Management workbook: 14 sheets / 82,847 validated cells
- Analytical Detail workbook: 16 sheets / 433,816 validated cells
- SQL validation: PASS
- Reference reconciliation: PASS

## Reference analytical baselines

- Sales Revenue: 19,701,685.507
- Units Sold: 11,221,960
- Orders: 39,519
- Sales Customers: 5,852
- Cancellation Value: 719,692.94
- Cancellation Value Rate: 3.5242%
- Anonymous Sales Revenue: 2,576,013.46
- Operational Adjustment Rows: 3,392
- Canonical Transaction Rows: 1,044,848

Evidence source:

`outputs/management/management_export_validation.json`

## Workbook reproduction

With SQL Server and the governed analytical model available:

```powershell
python src/exports/management_export.py
python src/exports/management_export.py --validate-only
```

The export recomputes SQL baselines, validates retained references, reconciles analytical rollups, and checks saved workbook cells against fresh SQL results.

## Interpretation rule

A successful current GitHub Action means the committed source and evidence package are internally consistent with the protected release contract.

It does **not** by itself mean that SQL Server, Power BI Desktop, or the external UCI workbook were freshly executed in GitHub Actions.

Checkpoint-specific SQL, Python, Power BI, and semantic evidence remains under `docs/validation/` for audit history.
