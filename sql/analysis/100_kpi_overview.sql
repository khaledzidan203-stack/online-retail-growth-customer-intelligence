USE [OnlineRetailAnalytics];
GO

CREATE OR ALTER VIEW analytics.vw_KPI_Overview
AS
WITH Sales AS
(
    SELECT
        SUM(LineAmount) AS SalesRevenue,
        SUM(CONVERT(BIGINT, Quantity)) AS UnitsSold,
        COUNT_BIG(*) AS SalesEligibleRows,
        COUNT(DISTINCT Invoice) AS Orders,
        COUNT(DISTINCT CustomerKey) AS KnownCustomers
    FROM analytics.FactTransaction
    WHERE IsSalesEligible = 1
),
CustomerOrders AS
(
    SELECT
        CustomerKey,
        COUNT(DISTINCT Invoice) AS Orders,
        SUM(LineAmount) AS Revenue,
        SUM(CONVERT(BIGINT, Quantity)) AS Units
    FROM analytics.FactTransaction
    WHERE IsCustomerAnalyticsEligible = 1
    GROUP BY CustomerKey
),
CustomerSummary AS
(
    SELECT
        COUNT_BIG(*) AS SalesKnownCustomers,
        SUM(CASE WHEN Orders = 1 THEN 1 ELSE 0 END) AS OneTimeCustomers,
        SUM(CASE WHEN Orders > 1 THEN 1 ELSE 0 END) AS RepeatCustomers,
        SUM(Orders) AS KnownCustomerOrders,
        SUM(Revenue) AS KnownCustomerRevenue,
        SUM(Units) AS KnownCustomerUnits
    FROM CustomerOrders
),
Cancellation AS
(
    SELECT
        SUM(ABS(LineAmount)) AS CancellationValue,
        SUM(ABS(CONVERT(BIGINT, Quantity))) AS CancellationUnits,
        COUNT_BIG(*) AS CancellationEligibleRows,
        COUNT(DISTINCT Invoice) AS CancellationInvoices,
        COUNT(DISTINCT CustomerKey) AS CustomersWithCancellations
    FROM analytics.FactTransaction
    WHERE IsCancellationEligible = 1
)
SELECT
    Sales.SalesRevenue,
    Sales.UnitsSold,
    Sales.SalesEligibleRows,
    Sales.Orders,
    Sales.KnownCustomers,
    CAST(Sales.SalesRevenue / NULLIF(Sales.Orders, 0) AS DECIMAL(28,8))
        AS AverageOrderValue,
    CAST(
        CONVERT(DECIMAL(28,8), Sales.UnitsSold)
        / NULLIF(Sales.Orders, 0)
        AS DECIMAL(28,8)
    ) AS AverageUnitsPerOrder,
    CustomerSummary.OneTimeCustomers,
    CustomerSummary.RepeatCustomers,
    CAST(
        CONVERT(DECIMAL(28,8), CustomerSummary.RepeatCustomers)
        / NULLIF(CustomerSummary.SalesKnownCustomers, 0)
        AS DECIMAL(28,8)
    ) AS RepeatCustomerRate,
    CAST(
        CONVERT(DECIMAL(28,8), CustomerSummary.KnownCustomerOrders)
        / NULLIF(CustomerSummary.SalesKnownCustomers, 0)
        AS DECIMAL(28,8)
    ) AS AveragePurchaseFrequency,
    CAST(
        CustomerSummary.KnownCustomerRevenue
        / NULLIF(CustomerSummary.SalesKnownCustomers, 0)
        AS DECIMAL(28,8)
    ) AS RevenuePerKnownCustomer,
    CAST(
        CONVERT(DECIMAL(28,8), CustomerSummary.KnownCustomerOrders)
        / NULLIF(CustomerSummary.SalesKnownCustomers, 0)
        AS DECIMAL(28,8)
    ) AS OrdersPerKnownCustomer,
    CustomerSummary.SalesKnownCustomers,
    CustomerSummary.KnownCustomerOrders,
    CustomerSummary.KnownCustomerRevenue,
    CustomerSummary.KnownCustomerUnits,
    Cancellation.CancellationValue,
    Cancellation.CancellationUnits,
    Cancellation.CancellationEligibleRows,
    Cancellation.CancellationInvoices,
    Cancellation.CustomersWithCancellations,
    CAST(
        Cancellation.CancellationValue
        / NULLIF(
            Sales.SalesRevenue + Cancellation.CancellationValue,
            0
        )
        AS DECIMAL(28,8)
    ) AS CancellationValueRate,
    (SELECT COUNT_BIG(*) FROM analytics.DimCustomer) AS ModelKnownCustomers
FROM Sales
CROSS JOIN CustomerSummary
CROSS JOIN Cancellation;
GO
