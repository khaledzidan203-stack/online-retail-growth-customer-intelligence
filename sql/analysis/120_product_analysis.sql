USE [OnlineRetailAnalytics];
GO

CREATE OR ALTER VIEW analytics.vw_ProductPerformance
AS
WITH ProductMetrics AS
(
    SELECT
        product.ProductKey,
        product.StockCode,
        product.RepresentativeDescription,
        product.ItemClass,
        SUM(CASE WHEN fact.IsSalesEligible = 1
            THEN fact.LineAmount ELSE 0 END) AS SalesRevenue,
        SUM(CASE WHEN fact.IsSalesEligible = 1
            THEN CONVERT(BIGINT, fact.Quantity) ELSE 0 END) AS UnitsSold,
        COUNT(DISTINCT CASE WHEN fact.IsSalesEligible = 1
            THEN fact.Invoice END) AS Orders,
        COUNT(DISTINCT CASE WHEN fact.IsCustomerAnalyticsEligible = 1
            THEN fact.CustomerKey END) AS KnownCustomers,
        SUM(CASE WHEN fact.IsCancellationEligible = 1
            THEN ABS(fact.LineAmount) ELSE 0 END) AS CancellationValue,
        SUM(CASE WHEN fact.IsCancellationEligible = 1
            THEN ABS(CONVERT(BIGINT, fact.Quantity)) ELSE 0 END)
            AS CancellationUnits
    FROM analytics.DimProduct AS product
    LEFT JOIN analytics.FactTransaction AS fact
        ON fact.ProductKey = product.ProductKey
    WHERE product.ItemClass = N'MERCHANDISE'
    GROUP BY
        product.ProductKey,
        product.StockCode,
        product.RepresentativeDescription,
        product.ItemClass
)
SELECT
    ProductKey,
    StockCode,
    RepresentativeDescription,
    ItemClass,
    SalesRevenue,
    UnitsSold,
    Orders,
    KnownCustomers,
    CAST(
        SalesRevenue / NULLIF(UnitsSold, 0)
        AS DECIMAL(28,8)
    ) AS AverageUnitPrice,
    CancellationValue,
    CancellationUnits,
    CAST(
        SalesRevenue / NULLIF(SUM(SalesRevenue) OVER (), 0)
        AS DECIMAL(28,10)
    ) AS RevenueShare,
    CAST(
        SUM(SalesRevenue) OVER
        (
            ORDER BY SalesRevenue DESC, StockCode ASC
            ROWS UNBOUNDED PRECEDING
        )
        / NULLIF(SUM(SalesRevenue) OVER (), 0)
        AS DECIMAL(28,10)
    ) AS CumulativeRevenueShare,
    ROW_NUMBER() OVER
    (
        ORDER BY SalesRevenue DESC, StockCode ASC
    ) AS RevenueRank,
    ROW_NUMBER() OVER
    (
        ORDER BY UnitsSold DESC, StockCode ASC
    ) AS UnitsRank,
    ROW_NUMBER() OVER
    (
        ORDER BY Orders DESC, StockCode ASC
    ) AS OrdersRank,
    ROW_NUMBER() OVER
    (
        ORDER BY KnownCustomers DESC, StockCode ASC
    ) AS KnownCustomerRank
FROM ProductMetrics;
GO
