# Architecture

~~~mermaid
flowchart TD
 A[UCI workbook] --> B[Python profiling and cleaning]
 B --> C[SQL raw]
 C --> D[SQL staging]
 D --> E[Analytics dimensions and fact]
 E --> F[Customer repeat, RFM and cohorts]
 E --> G[Power BI semantic model]
 F --> G
 G --> H[PBIP and PBIR report]
 E --> I[Python SQL export]
 I --> J[Management Excel workbooks]
 E --> K[Reconciliation and QA]
~~~

The raw source and canonical extract are excluded from Git. See [dataset handling](../data/README.md), [SQL execution order](sql_model.md), [star schema](architecture/SQL_STAR_SCHEMA.md) and [BI analytical layer](architecture/BI_ANALYTICAL_LAYER.md).
