# Contributing

Improvements are welcome when they preserve analytical correctness, evidence traceability, and publication safety.

## Development principles

1. Keep transaction classification and KPI definitions explicit.
2. Preserve fact and customer/cohort grains.
3. Add regression coverage when changing model logic.
4. Do not claim fresh SQL Server or Power BI runtime validation unless those runtimes were actually executed.
5. Keep raw/local data exclusions intact.
6. Do not alter protected validated artifacts as part of presentation-only changes.
7. Update evidence documentation when implementation boundaries change.

## Local public-repository checks

```bash
python scripts/validate_repository.py
python -m unittest discover -s tests -p "test_*.py" -v
python -m compileall -q src scripts tests
```

## Full analytical reproduction

A full reproduction additionally requires the official UCI Online Retail II workbook, SQL Server, ODBC connectivity, and compatible Power BI Desktop.

See the root README for the ordered pipeline.
