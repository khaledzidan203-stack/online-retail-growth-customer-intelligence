# Data dictionary

Field-level source and canonical definitions are in [DATA_DICTIONARY.md](discovery/DATA_DICTIONARY.md); SQL object grains and types are in [SQL_STAR_SCHEMA.md](architecture/SQL_STAR_SCHEMA.md).

| Object | Grain |
|---|---|
| FactTransaction | Governed canonical transaction line |
| DimDate | Calendar date |
| DimCustomer | Known customer |
| DimProduct | Normalized stock code |
| DimCountry | Recorded country |
| CustomerRFM | Published customer snapshot |
| CustomerCohort | Customer acquisition cohort |
| CustomerRepeatBehavior | Customer repeat-purchase result |
| CohortRetention / CohortRevenue | Published cohort-period cells; disconnected in Power BI |

Unknown customer IDs are preserved in the fact and do not receive fabricated dimension members.
