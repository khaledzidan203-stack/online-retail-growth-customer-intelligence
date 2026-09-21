USE [OnlineRetailAnalytics];
GO

CREATE OR ALTER VIEW analytics.vw_CountryPerformance
AS
WITH CountryMetrics AS
(
    SELECT
        country.CountryKey,
        country.Country,
        SUM(CASE WHEN fact.IsSalesEligible = 1
            THEN fact.LineAmount ELSE 0 END) AS SalesRevenue,
        SUM(CASE WHEN fact.IsSalesEligible = 1
            THEN CONVERT(BIGINT, fact.Quantity) ELSE 0 END) AS UnitsSold,
        COUNT(DISTINCT CASE WHEN fact.IsSalesEligible = 1
            THEN fact.Invoice END) AS Orders,
        COUNT(DISTINCT CASE WHEN fact.IsCustomerAnalyticsEligible = 1
            THEN fact.CustomerKey END) AS KnownCustomers,
        SUM(CASE WHEN fact.IsCancellationEligible = 1
            THEN ABS(fact.LineAmount) ELSE 0 END) AS CancellationValue
    FROM analytics.DimCountry AS country
    LEFT JOIN analytics.FactTransaction AS fact
        ON fact.CountryKey = country.CountryKey
    GROUP BY
        country.CountryKey,
        country.Country
)
SELECT
    CountryKey,
    Country,
    SalesRevenue,
    Orders,
    UnitsSold,
    KnownCustomers,
    CAST(
        SalesRevenue / NULLIF(Orders, 0)
        AS DECIMAL(28,8)
    ) AS AverageOrderValue,
    CAST(
        SalesRevenue / NULLIF(KnownCustomers, 0)
        AS DECIMAL(28,8)
    ) AS RevenuePerKnownCustomer,
    CancellationValue,
    CAST(
        CancellationValue
        / NULLIF(SalesRevenue + CancellationValue, 0)
        AS DECIMAL(28,8)
    ) AS CancellationValueRate,
    CAST(
        SalesRevenue / NULLIF(SUM(SalesRevenue) OVER (), 0)
        AS DECIMAL(28,10)
    ) AS RevenueShare,
    CAST(
        SUM(SalesRevenue) OVER
        (
            ORDER BY SalesRevenue DESC, Country ASC
            ROWS UNBOUNDED PRECEDING
        )
        / NULLIF(SUM(SalesRevenue) OVER (), 0)
        AS DECIMAL(28,10)
    ) AS CumulativeRevenueShare,
    ROW_NUMBER() OVER
    (
        ORDER BY SalesRevenue DESC, Country ASC
    ) AS RevenueRank,
    CONVERT(BIT, CASE WHEN Orders >= 100 THEN 1 ELSE 0 END)
        AS MeetsCancellationRateMinimumBase
FROM CountryMetrics;
GO
