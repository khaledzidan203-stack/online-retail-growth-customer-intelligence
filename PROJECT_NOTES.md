# Project Notes

## Purpose

Online Retail Growth & Customer Intelligence is an end-to-end retail analytics system built from the public UCI Online Retail II dataset.

The implementation spans source profiling, transaction governance, SQL Server dimensional modeling, customer analytics, Power BI semantic/report engineering, and validated Excel management outputs.

## Core design choices

1. **Transaction governance before reporting** — merchandise sales, cancellations, operational adjustments, accounting adjustments, zero-price lines, tests, anonymous sales, and duplicate exposure are classified explicitly.
2. **Fact grain remains transaction line** — downstream models retain lineage to canonical transactions.
3. **Customer analytics use compatible grains** — RFM, cohort, and repeat-purchase outputs are modeled separately from the transaction fact.
4. **Disconnected cohort result tables are intentional** — cohort-period aggregates are not forced into incompatible fact relationships.
5. **Anonymous sales remain in sales revenue** — customer-level analysis excludes unknown customer IDs without deleting valid sales activity.
6. **Cancellations remain separate from sales** — cancellation exposure is not netted silently into the merchandise-sales baseline.
7. **Power BI source is version-controlled** — PBIP, PBIR, TMDL, DAX, and report definitions are committed.
8. **Excel management outputs come from SQL, not report visuals** — workbook validation reconciles saved cells to fresh SQL queries in the retained validation record.
9. **No unsupported profitability claim** — the source does not provide reliable COGS, marketing spend, or inventory valuation.

## Implemented layers

- UCI source acquisition instructions;
- Python profiling and canonical transaction construction;
- SQL Server raw, staging, dimensions, fact, customer analytics, and validation;
- Python EDA, RFM, cohort, publishing, and exports;
- Power BI PBIP/PBIR/TMDL source;
- 10-page report;
- two validated Excel management workbooks;
- authentic report screenshots;
- retained analytical reconciliation evidence.

## Current publication boundary

The raw UCI workbook and local canonical Parquet are intentionally excluded from Git.

The public repository retains source code, model source, screenshots, workbooks, and validation records.

GitHub CI can validate committed artifacts but cannot prove a fresh Power BI Desktop refresh or full SQL Server execution unless those runtimes are explicitly provisioned.
