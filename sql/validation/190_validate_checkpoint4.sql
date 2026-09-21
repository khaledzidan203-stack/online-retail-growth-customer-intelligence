USE [OnlineRetailAnalytics];
GO

SET NOCOUNT ON;

DECLARE @Results TABLE
(
    SortOrder INT NOT NULL,
    Metric NVARCHAR(200) NOT NULL,
    ActualValue DECIMAL(38,8) NOT NULL,
    ExpectedValue DECIMAL(38,8) NOT NULL
);

INSERT INTO @Results VALUES
(10, N'Sales Revenue',
    (SELECT SalesRevenue FROM analytics.vw_KPI_Overview),
    19701685.507),
(20, N'Sales eligible rows',
    (SELECT SalesEligibleRows FROM analytics.vw_KPI_Overview),
    1015091),
(30, N'Sales eligible Orders',
    (SELECT Orders FROM analytics.vw_KPI_Overview),
    39519),
(40, N'Cancellation Value',
    (SELECT CancellationValue FROM analytics.vw_KPI_Overview),
    719692.94),
(50, N'Cancellation eligible rows',
    (SELECT CancellationEligibleRows
     FROM analytics.vw_KPI_Overview),
    17974),
(60, N'Known Customer population',
    (SELECT ModelKnownCustomers FROM analytics.vw_KPI_Overview),
    5942),
(100, N'Product revenue reconciles to merchandise sales',
    (SELECT SUM(SalesRevenue)
     FROM analytics.vw_ProductPerformance),
    (SELECT SalesRevenue FROM analytics.vw_KPI_Overview)),
(110, N'Non-merchandise products in product ranking',
    (SELECT COUNT_BIG(*)
     FROM analytics.vw_ProductPerformance
     WHERE ItemClass <> N'MERCHANDISE'), 0),
(120, N'Customer revenue reconciles to known-customer sales',
    (SELECT SUM(SalesRevenue)
     FROM analytics.vw_CustomerPerformance),
    (SELECT SUM(LineAmount)
     FROM analytics.FactTransaction
     WHERE IsCustomerAnalyticsEligible = 1)),
(130, N'Missing Customer IDs in customer KPI view',
    (SELECT COUNT_BIG(*)
     FROM analytics.vw_CustomerPerformance
     WHERE CustomerID IS NULL), 0),
(140, N'One-time plus repeat customer reconciliation',
    (SELECT OneTimeCustomers + RepeatCustomers
     FROM analytics.vw_KPI_Overview),
    (SELECT SalesKnownCustomers FROM analytics.vw_KPI_Overview)),
(150, N'Operational adjustments in cancellation population',
    (SELECT COUNT_BIG(*)
     FROM analytics.FactTransaction
     WHERE IsCancellationEligible = 1
       AND TransactionClass = N'OPERATIONAL_STOCK_ADJUSTMENT'), 0),
(160, N'Monthly revenue reconciles to overall',
    (SELECT SUM(SalesRevenue)
     FROM analytics.vw_MonthlyPerformance),
    (SELECT SalesRevenue FROM analytics.vw_KPI_Overview)),
(170, N'Monthly cancellation value reconciles to overall',
    (SELECT SUM(CancellationValue)
     FROM analytics.vw_MonthlyPerformance),
    (SELECT CancellationValue FROM analytics.vw_KPI_Overview)),
(180, N'Country revenue reconciles to overall',
    (SELECT SUM(SalesRevenue)
     FROM analytics.vw_CountryPerformance),
    (SELECT SalesRevenue FROM analytics.vw_KPI_Overview)),
(190, N'Country cancellation value reconciles to overall',
    (SELECT SUM(CancellationValue)
     FROM analytics.vw_CountryPerformance),
    (SELECT CancellationValue FROM analytics.vw_KPI_Overview)),
(200, N'Cancellation view value reconciles to overall',
    (SELECT SUM(CancellationValue)
     FROM analytics.vw_CancellationPerformance),
    (SELECT CancellationValue FROM analytics.vw_KPI_Overview)),
(210, N'Customer revenue excluded from total for missing IDs',
    (SELECT SalesRevenue - KnownCustomerRevenue
     FROM analytics.vw_KPI_Overview),
    (SELECT SUM(LineAmount)
     FROM analytics.FactTransaction
     WHERE IsSalesEligible = 1
       AND CustomerKey IS NULL));

SELECT
    Metric,
    ActualValue,
    ExpectedValue,
    CASE WHEN ActualValue = ExpectedValue
        THEN N'PASS' ELSE N'FAIL' END AS ValidationStatus
FROM @Results
ORDER BY SortOrder;
GO
