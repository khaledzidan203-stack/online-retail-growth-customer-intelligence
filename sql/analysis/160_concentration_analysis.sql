USE [OnlineRetailAnalytics];
GO

-- Product concentration:
SELECT
    RevenueRank,
    StockCode,
    SalesRevenue,
    RevenueShare,
    CumulativeRevenueShare
FROM analytics.vw_ProductPerformance
WHERE SalesRevenue > 0;

-- Customer concentration:
SELECT
    RevenueRank,
    CustomerID,
    SalesRevenue,
    RevenueShare,
    CumulativeRevenueShare
FROM analytics.vw_CustomerPerformance;

-- Country concentration:
SELECT
    Country,
    SalesRevenue,
    RevenueShare
FROM analytics.vw_CountryPerformance;
GO
