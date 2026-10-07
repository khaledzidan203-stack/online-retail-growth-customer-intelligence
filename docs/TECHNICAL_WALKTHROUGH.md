# Technical Walkthrough — 60–90 Seconds

**0–10 seconds — Scope**

This is an end-to-end retail analytics project using the public UCI Online Retail II dataset, SQL Server, Python, Power BI, and validated Excel management outputs.

**10–25 seconds — Governance first**

Python profiling classifies transaction rows into merchandise sales, customer cancellations, non-merchandise, operational adjustments, zero-price merchandise, accounting adjustments, and test records before analytics are built.

**25–40 seconds — SQL model**

Canonical rows land in SQL raw/staging layers and are published into a star model with Date, Customer, Product, Country, and FactTransaction at transaction-line grain.

**40–55 seconds — Customer intelligence**

Python and SQL publish repeat-purchase, RFM, cohort, retention, and cohort-revenue outputs. Customer-level summaries stay at customer grain, while cohort result tables remain disconnected at cohort-period grain.

**55–70 seconds — Power BI**

The source-controlled PBIP project contains 10 pages, 136 visuals, 50 explicit DAX measures, 7 active single-direction relationships, and 15 TMDL files.

**70–80 seconds — Excel delivery**

Two SQL-driven management workbooks provide executive and detailed analytical exports. Retained validation records 82,847 and 433,816 validated cells respectively.

**80–90 seconds — Evidence boundary**

The repository retains completed analytical evidence, but current GitHub CI does not launch SQL Server or Power BI Desktop. Fresh CI validates the committed artifact structure, report/model source, workbook package structure, evidence baselines, and publication safety.
