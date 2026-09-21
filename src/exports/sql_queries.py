"""Read-only SQL for governed management exports. No database objects are created."""

KPI = "SELECT * FROM analytics.vw_KPI_Overview"
DQ = """
SELECT COUNT_BIG(*) AS CanonicalTransactionRows,
 SUM(CONVERT(bigint,IsSalesEligible)) AS SalesEligibleRows,
 SUM(CASE WHEN IsKnownCustomer=0 THEN CONVERT(bigint,1) ELSE 0 END) AS UnknownCustomerRows,
 SUM(CASE WHEN IsSalesEligible=1 AND IsKnownCustomer=0 THEN LineAmount ELSE 0 END) AS AnonymousSalesRevenue,
 SUM(CONVERT(bigint,IsZeroPrice)) AS ZeroPriceRows,
 SUM(CONVERT(bigint,IsNegativePrice)) AS NegativePriceRows,
 SUM(CONVERT(bigint,IsExactDuplicateAfterFirst)) AS ExactDuplicateAfterFirstRows,
 SUM(CONVERT(bigint,IsInExactDuplicateGroup)) AS RowsInDuplicateGroups,
 SUM(CASE WHEN IsSalesEligible=1 AND IsExactDuplicateAfterFirst=1 THEN LineAmount ELSE 0 END) AS DuplicateFlaggedRevenue,
 SUM(CASE WHEN TransactionClass='OPERATIONAL_STOCK_ADJUSTMENT' THEN CONVERT(bigint,1) ELSE 0 END) AS OperationalAdjustmentRows,
 SUM(CASE WHEN TransactionClass='ACCOUNTING_ADJUSTMENT' THEN CONVERT(bigint,1) ELSE 0 END) AS AccountingAdjustmentRows,
 SUM(CASE WHEN TransactionClass='DQ_REVIEW' THEN CONVERT(bigint,1) ELSE 0 END) AS DQReviewRows
FROM analytics.FactTransaction
"""
INDEPENDENT = """
SELECT SUM(CASE WHEN IsSalesEligible=1 THEN LineAmount ELSE 0 END) SalesRevenue,
 SUM(CASE WHEN IsSalesEligible=1 THEN CONVERT(bigint,Quantity) ELSE 0 END) UnitsSold,
 COUNT(DISTINCT CASE WHEN IsSalesEligible=1 THEN Invoice END) Orders,
 COUNT(DISTINCT CASE WHEN IsCustomerAnalyticsEligible=1 THEN CustomerKey END) SalesCustomers,
 SUM(CASE WHEN IsCancellationEligible=1 THEN ABS(LineAmount) ELSE 0 END) CancellationValue,
 SUM(CASE WHEN IsSalesEligible=1 AND IsKnownCustomer=0 THEN LineAmount ELSE 0 END) AnonymousSalesRevenue,
 SUM(CASE WHEN TransactionClass='OPERATIONAL_STOCK_ADJUSTMENT' THEN CONVERT(bigint,1) ELSE 0 END) OperationalAdjustmentRows,
 COUNT_BIG(*) CanonicalTransactionRows
FROM analytics.FactTransaction
"""
RELATIONSHIPS = """
SELECT fk.name ForeignKey, OBJECT_NAME(f.parent_object_id) FromTable,
 pc.name FromColumn, OBJECT_NAME(f.referenced_object_id) ToTable, rc.name ToColumn,
 'Many-to-one (unique on both sides for customer analytical tables)' Cardinality,
 CASE WHEN fk.is_disabled=0 THEN 'Enabled' ELSE 'Disabled' END ConstraintStatus
FROM sys.foreign_key_columns f
JOIN sys.foreign_keys fk ON fk.object_id=f.constraint_object_id
JOIN sys.columns pc ON pc.object_id=f.parent_object_id AND pc.column_id=f.parent_column_id
JOIN sys.columns rc ON rc.object_id=f.referenced_object_id AND rc.column_id=f.referenced_column_id
WHERE OBJECT_SCHEMA_NAME(f.parent_object_id)='analytics'
ORDER BY FromTable,ToTable
"""
CLASSES = """
SELECT TransactionClass, COUNT_BIG(*) AS [Rows], COUNT(DISTINCT Invoice) Invoices,
 SUM(CONVERT(bigint,Quantity)) NetQuantity, SUM(ABS(CONVERT(bigint,Quantity))) AbsoluteQuantity,
 SUM(LineAmount) NetValue, SUM(ABS(LineAmount)) AbsoluteValue
FROM analytics.FactTransaction GROUP BY TransactionClass ORDER BY [Rows] DESC,TransactionClass
"""
MARKETS = """
SELECT v.*, COALESCE(a.AnonymousSalesRevenue,0) AnonymousSalesRevenue
FROM analytics.vw_CountryPerformance v LEFT JOIN
 (SELECT CountryKey,SUM(LineAmount) AnonymousSalesRevenue FROM analytics.FactTransaction
  WHERE IsSalesEligible=1 AND IsKnownCustomer=0 GROUP BY CountryKey) a
ON a.CountryKey=v.CountryKey ORDER BY v.RevenueRank
"""
PRODUCTS = """
SELECT v.*, COALESCE(d.DuplicateFlaggedRevenue,0) DuplicateFlaggedRevenue
FROM analytics.vw_ProductPerformance v LEFT JOIN
 (SELECT ProductKey,SUM(LineAmount) DuplicateFlaggedRevenue FROM analytics.FactTransaction
  WHERE IsSalesEligible=1 AND IsExactDuplicateAfterFirst=1 GROUP BY ProductKey) d
ON d.ProductKey=v.ProductKey ORDER BY v.RevenueRank
"""
CUSTOMERS = """
SELECT p.CustomerID,p.SalesRevenue,p.Orders,p.Units,r.AverageOrderValue,
 p.FirstPurchaseDate,p.LastPurchaseDate,
 CASE WHEN b.HasRepeatPurchase=1 THEN 'Repeat' ELSE 'One-Time' END PurchaseBehavior,
 r.Segment,r.Recency,r.Frequency,r.Monetary,p.RevenueRank
FROM analytics.vw_CustomerPerformance p JOIN analytics.CustomerRFM r ON r.CustomerKey=p.CustomerKey
JOIN analytics.CustomerRepeatBehavior b ON b.CustomerKey=p.CustomerKey ORDER BY p.RevenueRank
"""
RFM_SEGMENTS = """
SELECT Segment,COUNT_BIG(*) Customers,SUM(Monetary) Revenue,SUM(CONVERT(bigint,Frequency)) Orders,
 AVG(Monetary) AverageRevenuePerCustomer,AVG(CONVERT(decimal(18,6),Frequency)) AverageFrequency,
 AVG(CONVERT(decimal(18,6),Recency)) AverageRecency
FROM analytics.CustomerRFM GROUP BY Segment ORDER BY Revenue DESC,Segment
"""
def cancellation_dimension(dimension, key, labels):
    return f"""SELECT {labels},
    COUNT(DISTINCT CASE WHEN f.IsCancellationEligible=1 THEN f.Invoice END) CancellationInvoices,
    COUNT(DISTINCT CASE WHEN f.IsCancellationEligible=1 AND f.IsKnownCustomer=1 THEN f.CustomerKey END) CustomersWithCancellations,
    SUM(CASE WHEN f.IsCancellationEligible=1 THEN ABS(CONVERT(bigint,f.Quantity)) ELSE 0 END) CancellationUnits,
    SUM(CASE WHEN f.IsCancellationEligible=1 THEN ABS(f.LineAmount) ELSE 0 END) CancellationValue,
    SUM(CASE WHEN f.IsSalesEligible=1 THEN f.LineAmount ELSE 0 END) SalesRevenue,
    CONVERT(float,SUM(CASE WHEN f.IsCancellationEligible=1 THEN ABS(f.LineAmount) ELSE 0 END)) /
    NULLIF(SUM(CASE WHEN f.IsSalesEligible=1 THEN f.LineAmount WHEN f.IsCancellationEligible=1 THEN ABS(f.LineAmount) ELSE 0 END),0) CancellationValueRate
    FROM analytics.FactTransaction f JOIN analytics.{dimension} d ON d.{key}=f.{key}
    GROUP BY {labels} ORDER BY CancellationValue DESC,{labels}"""

QUERIES = {
 'CUSTOMER_360': 'SELECT * FROM analytics.vw_Customer360 ORDER BY CustomerID',
 'CUSTOMER_RFM': 'SELECT * FROM analytics.CustomerRFM ORDER BY Monetary DESC,CustomerID',
 'CUSTOMER_COHORT': 'SELECT * FROM analytics.CustomerCohort ORDER BY AcquisitionCohort,CustomerID',
 'CUSTOMER_REPEAT_BEHAVIOR': 'SELECT * FROM analytics.CustomerRepeatBehavior ORDER BY CustomerID',
 'COHORT_RETENTION': 'SELECT * FROM analytics.CohortRetention ORDER BY AcquisitionCohort,CohortIndex',
 'COHORT_REVENUE': 'SELECT * FROM analytics.CohortRevenue ORDER BY AcquisitionCohort,CohortIndex',
 'PRODUCT_ANALYTICS': PRODUCTS, 'MARKET_ANALYTICS': MARKETS,
 'MONTHLY_SALES': 'SELECT * FROM analytics.vw_MonthlyPerformance ORDER BY PeriodStart',
 'CANCELLATION_PRODUCTS': cancellation_dimension('DimProduct','ProductKey','d.StockCode,d.RepresentativeDescription'),
 'CANCELLATION_MARKETS': cancellation_dimension('DimCountry','CountryKey','d.Country'),
 'MONTHLY_CANCELLATIONS': 'SELECT * FROM analytics.vw_CancellationPerformance ORDER BY PeriodStart',
 'ANONYMOUS_MARKETS': """SELECT c.Country,COUNT_BIG(*) SalesRows,COUNT(DISTINCT f.Invoice) Orders,
 SUM(f.LineAmount) AnonymousSalesRevenue,SUM(CONVERT(bigint,f.Quantity)) Units
 FROM analytics.FactTransaction f JOIN analytics.DimCountry c ON c.CountryKey=f.CountryKey
 WHERE f.IsSalesEligible=1 AND f.IsKnownCustomer=0 GROUP BY c.Country ORDER BY AnonymousSalesRevenue DESC""",
 'DUPLICATE_EXPOSURE': """SELECT f.TransactionClass,COUNT_BIG(*) DuplicateAfterFirstRows,
 SUM(f.LineAmount) NetValue,SUM(CASE WHEN IsSalesEligible=1 THEN LineAmount ELSE 0 END) DuplicateFlaggedRevenue,
 SUM(CONVERT(bigint,Quantity)) NetQuantity FROM analytics.FactTransaction f
 WHERE IsExactDuplicateAfterFirst=1 GROUP BY f.TransactionClass ORDER BY DuplicateAfterFirstRows DESC,f.TransactionClass""",
 'TRANSACTION_CLASS_DETAIL': CLASSES,
}
