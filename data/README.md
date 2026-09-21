# Dataset and local data policy

The source is **UCI Online Retail II**: Chen, D. (2012), UCI Machine Learning Repository, [DOI: 10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D). Obtain the workbook from the [official dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii). UCI identifies its license as CC BY 4.0.

## Reproduce

1. Download and extract the original workbook.
2. Place the file at `data/raw/online_retail_II.xlsx`.
3. Run `python src/ingestion/profile_raw_dataset.py`.
4. Run `python src/cleaning/build_canonical_transactions.py`.
5. Continue with SQL loading and analytics in the root [reproduction guide](../README.md#reproduce-the-project).

The raw workbook and derived canonical Parquet are deliberately excluded from Git. They are not deleted locally. The public portfolio contains code, governed derived outputs, documentation and real report screenshots.

Project monetary values are reported as source-currency units. Raw source row counts and governed canonical row counts are different stages; the project's canonical baseline is 1,044,848 transaction rows.
