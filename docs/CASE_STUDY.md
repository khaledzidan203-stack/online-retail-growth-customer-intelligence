# Case Study — Online Retail Growth & Customer Intelligence

## Context

Retail transaction datasets often mix normal sales, cancellations, non-merchandise rows, operational stock movements, accounting adjustments, duplicate exposure, anonymous purchases, and zero-price records.

Treating all rows as one undifferentiated revenue fact can distort customer, product, market, and retention analysis.

This project first governs transaction classes, then builds analytical models and report outputs on top of that governed baseline.

## Source

The project uses the public **UCI Online Retail II** dataset.

The raw workbook is intentionally excluded from Git and is downloaded separately from the official source.

## Canonical analytical baseline

Retained validation evidence records:

- Canonical transaction rows: **1,044,848**
- Sales Revenue: **19,701,685.507** source-currency units
- Units Sold: **11,221,960**
- Orders: **39,519**
- Known sales customers: **5,852**
- Repeat customers: **4,234**
- One-time customers: **1,618**
- Repeat Customer Rate: **72.35%**
- Cancellation Value: **719,692.94**
- Cancellation Value Rate: **3.5242%**
- Anonymous Sales Revenue: **2,576,013.46**
- Operational adjustment rows: **3,392**

These values come from retained SQL/Excel reconciliation evidence and are not recalculated by current GitHub CI.

## Governance model

Rows are classified into governed categories:

- MERCHANDISE_SALE
- CUSTOMER_CANCELLATION
- NON_MERCHANDISE
- OPERATIONAL_STOCK_ADJUSTMENT
- ZERO_PRICE_MERCHANDISE
- ACCOUNTING_ADJUSTMENT
- TEST_RECORD

Sales, cancellations, and operational/accounting exceptions are therefore available for separate analysis.

## Analytical architecture

`Raw UCI workbook → Python profiling/classification → canonical transactions → SQL raw/staging → dimensional analytics → customer analytics → Power BI + Excel deliverables → validation evidence`

## Customer intelligence

The project publishes:

- repeat-purchase behavior;
- customer performance;
- RFM segmentation;
- cohort assignment;
- cohort retention;
- cohort revenue.

RFM is a snapshot.

CohortRetention and CohortRevenue remain disconnected in Power BI because they operate at acquisition-cohort × cohort-index grain.

## Power BI implementation

The repository contains actual source-controlled Power BI artifacts:

- PBIP project;
- PBIR report source;
- TMDL semantic model;
- 10 pages;
- 136 visuals;
- 50 explicit measures;
- 7 active single-direction relationships;
- 15 TMDL files.

Ten authentic report screenshots are retained.

## Management deliverables

Two generated Excel workbooks are retained:

- Management Analytics — 14 sheets
- Analytical Detail — 16 sheets

The validation JSON records:

- SQL validation: PASS
- reference reconciliation: PASS
- 82,847 validated management cells
- 433,816 validated detail cells

## Interpretation boundaries

- Monetary values remain source-currency units; no currency conversion is claimed.
- The dataset does not support reliable COGS, Profit, Gross Margin, Inventory Valuation, ROI, or Marketing-Spend analysis.
- Duplicate exposure is measured rather than silently removed.
- Anonymous sales remain part of sales revenue.
- Partial observation years affect cohort interpretation.
- Descriptive findings are not causal claims.
