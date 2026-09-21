USE [OnlineRetailAnalytics];
GO

CREATE OR ALTER VIEW analytics.vw_CustomerPerformance
AS
WITH CustomerMetrics AS
(
    SELECT
        customer.CustomerKey,
        customer.CustomerID,
        SUM(fact.LineAmount) AS SalesRevenue,
        COUNT(DISTINCT fact.Invoice) AS Orders,
        SUM(CONVERT(BIGINT, fact.Quantity)) AS Units,
        MIN(CONVERT(DATE, fact.InvoiceDate)) AS FirstPurchaseDate,
        MAX(CONVERT(DATE, fact.InvoiceDate)) AS LastPurchaseDate
    FROM analytics.DimCustomer AS customer
    INNER JOIN analytics.FactTransaction AS fact
        ON fact.CustomerKey = customer.CustomerKey
       AND fact.IsCustomerAnalyticsEligible = 1
    GROUP BY
        customer.CustomerKey,
        customer.CustomerID
)
SELECT
    CustomerKey,
    CustomerID,
    SalesRevenue,
    Orders,
    Units,
    FirstPurchaseDate,
    LastPurchaseDate,
    DATEDIFF(DAY, FirstPurchaseDate, LastPurchaseDate)
        AS ActiveLifespanDays,
    CAST(
        SalesRevenue / NULLIF(SUM(SalesRevenue) OVER (), 0)
        AS DECIMAL(28,10)
    ) AS RevenueShare,
    CAST(
        SUM(SalesRevenue) OVER
        (
            ORDER BY SalesRevenue DESC, CustomerID ASC
            ROWS UNBOUNDED PRECEDING
        )
        / NULLIF(SUM(SalesRevenue) OVER (), 0)
        AS DECIMAL(28,10)
    ) AS CumulativeRevenueShare,
    ROW_NUMBER() OVER
    (
        ORDER BY SalesRevenue DESC, CustomerID ASC
    ) AS RevenueRank
FROM CustomerMetrics;
GO
