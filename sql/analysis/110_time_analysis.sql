USE [OnlineRetailAnalytics];
GO

CREATE OR ALTER VIEW analytics.vw_MonthlyPerformance
AS
SELECT
    DATEFROMPARTS(date_dimension.[Year], date_dimension.MonthNumber, 1)
        AS PeriodStart,
    date_dimension.YearMonth,
    date_dimension.[Year],
    date_dimension.MonthNumber,
    SUM(CASE WHEN fact.IsSalesEligible = 1
        THEN fact.LineAmount ELSE 0 END) AS SalesRevenue,
    SUM(CASE WHEN fact.IsSalesEligible = 1
        THEN CONVERT(BIGINT, fact.Quantity) ELSE 0 END) AS UnitsSold,
    COUNT(DISTINCT CASE WHEN fact.IsSalesEligible = 1
        THEN fact.Invoice END) AS Orders,
    COUNT(DISTINCT CASE WHEN fact.IsCustomerAnalyticsEligible = 1
        THEN fact.CustomerKey END) AS KnownCustomers,
    CAST(
        SUM(CASE WHEN fact.IsSalesEligible = 1
            THEN fact.LineAmount ELSE 0 END)
        / NULLIF(
            COUNT(DISTINCT CASE WHEN fact.IsSalesEligible = 1
                THEN fact.Invoice END),
            0
        )
        AS DECIMAL(28,8)
    ) AS AverageOrderValue,
    SUM(CASE WHEN fact.IsCancellationEligible = 1
        THEN ABS(fact.LineAmount) ELSE 0 END) AS CancellationValue,
    SUM(CASE WHEN fact.IsCancellationEligible = 1
        THEN ABS(CONVERT(BIGINT, fact.Quantity)) ELSE 0 END)
        AS CancellationUnits,
    COUNT(DISTINCT CASE WHEN fact.IsCancellationEligible = 1
        THEN fact.Invoice END) AS CancellationInvoices,
    CAST(
        SUM(CASE WHEN fact.IsCancellationEligible = 1
            THEN ABS(fact.LineAmount) ELSE 0 END)
        / NULLIF(
            SUM(CASE WHEN fact.IsSalesEligible = 1
                THEN fact.LineAmount ELSE 0 END)
            + SUM(CASE WHEN fact.IsCancellationEligible = 1
                THEN ABS(fact.LineAmount) ELSE 0 END),
            0
        )
        AS DECIMAL(28,8)
    ) AS CancellationValueRate
FROM analytics.FactTransaction AS fact
INNER JOIN analytics.DimDate AS date_dimension
    ON date_dimension.DateKey = fact.DateKey
GROUP BY
    date_dimension.[Year],
    date_dimension.MonthNumber,
    date_dimension.YearMonth;
GO

CREATE OR ALTER VIEW analytics.vw_TimePerformance
AS
SELECT
    CASE
        WHEN GROUPING(date_dimension.[Year]) = 0
         AND GROUPING(date_dimension.[Quarter]) = 1 THEN N'YEAR'
        WHEN GROUPING(date_dimension.[Quarter]) = 0 THEN N'QUARTER'
        WHEN GROUPING(date_dimension.DayOfWeekNumber) = 0
            THEN N'DAY_OF_WEEK'
        ELSE N'HOUR_OF_DAY'
    END AS PeriodType,
    CASE
        WHEN GROUPING(date_dimension.[Year]) = 0
         AND GROUPING(date_dimension.[Quarter]) = 1
            THEN CONVERT(NVARCHAR(20), date_dimension.[Year])
        WHEN GROUPING(date_dimension.[Quarter]) = 0
            THEN CONCAT(date_dimension.[Year], N'-Q', date_dimension.[Quarter])
        WHEN GROUPING(date_dimension.DayOfWeekNumber) = 0
            THEN CONCAT(N'DOW-', date_dimension.DayOfWeekNumber)
        ELSE CONCAT(
            N'HOUR-',
            RIGHT(N'0' + CONVERT(
                NVARCHAR(2), DATEPART(HOUR, fact.InvoiceDate)
            ), 2)
        )
    END AS PeriodKey,
    date_dimension.[Year],
    date_dimension.[Quarter],
    date_dimension.DayOfWeekNumber,
    CASE WHEN GROUPING(date_dimension.DayName) = 0
        THEN date_dimension.DayName END AS DayName,
    CASE WHEN GROUPING(DATEPART(HOUR, fact.InvoiceDate)) = 0
        THEN DATEPART(HOUR, fact.InvoiceDate) END AS HourOfDay,
    SUM(CASE WHEN fact.IsSalesEligible = 1
        THEN fact.LineAmount ELSE 0 END) AS SalesRevenue,
    SUM(CASE WHEN fact.IsSalesEligible = 1
        THEN CONVERT(BIGINT, fact.Quantity) ELSE 0 END) AS UnitsSold,
    COUNT(DISTINCT CASE WHEN fact.IsSalesEligible = 1
        THEN fact.Invoice END) AS Orders,
    COUNT(DISTINCT CASE WHEN fact.IsCustomerAnalyticsEligible = 1
        THEN fact.CustomerKey END) AS KnownCustomers,
    CAST(
        SUM(CASE WHEN fact.IsSalesEligible = 1
            THEN fact.LineAmount ELSE 0 END)
        / NULLIF(COUNT(DISTINCT CASE WHEN fact.IsSalesEligible = 1
            THEN fact.Invoice END), 0)
        AS DECIMAL(28,8)
    ) AS AverageOrderValue,
    SUM(CASE WHEN fact.IsCancellationEligible = 1
        THEN ABS(fact.LineAmount) ELSE 0 END) AS CancellationValue,
    CAST(
        SUM(CASE WHEN fact.IsCancellationEligible = 1
            THEN ABS(fact.LineAmount) ELSE 0 END)
        / NULLIF(
            SUM(CASE WHEN fact.IsSalesEligible = 1
                THEN fact.LineAmount ELSE 0 END)
            + SUM(CASE WHEN fact.IsCancellationEligible = 1
                THEN ABS(fact.LineAmount) ELSE 0 END),
            0
        )
        AS DECIMAL(28,8)
    ) AS CancellationValueRate
FROM analytics.FactTransaction AS fact
INNER JOIN analytics.DimDate AS date_dimension
    ON date_dimension.DateKey = fact.DateKey
GROUP BY GROUPING SETS
(
    (date_dimension.[Year]),
    (date_dimension.[Year], date_dimension.[Quarter]),
    (date_dimension.DayOfWeekNumber, date_dimension.DayName),
    (DATEPART(HOUR, fact.InvoiceDate))
);
GO
