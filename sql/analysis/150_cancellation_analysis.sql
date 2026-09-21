USE [OnlineRetailAnalytics];
GO

CREATE OR ALTER VIEW analytics.vw_CancellationPerformance
AS
SELECT
    DATEFROMPARTS(date_dimension.[Year], date_dimension.MonthNumber, 1)
        AS PeriodStart,
    date_dimension.YearMonth,
    SUM(CASE WHEN fact.IsCancellationEligible = 1
        THEN ABS(fact.LineAmount) ELSE 0 END) AS CancellationValue,
    SUM(CASE WHEN fact.IsCancellationEligible = 1
        THEN ABS(CONVERT(BIGINT, fact.Quantity)) ELSE 0 END)
        AS CancellationUnits,
    COUNT(DISTINCT CASE WHEN fact.IsCancellationEligible = 1
        THEN fact.Invoice END) AS CancellationInvoices,
    COUNT(DISTINCT CASE WHEN fact.IsCancellationEligible = 1
        THEN fact.CustomerKey END) AS KnownCustomersWithCancellations,
    SUM(CASE WHEN fact.IsSalesEligible = 1
        THEN fact.LineAmount ELSE 0 END) AS SalesRevenue,
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
    ) AS CancellationValueRate,
    SUM(CASE WHEN fact.TransactionClass =
        N'OPERATIONAL_STOCK_ADJUSTMENT' THEN 1 ELSE 0 END)
        AS OperationalAdjustmentRows,
    SUM(CASE WHEN fact.TransactionClass =
        N'OPERATIONAL_STOCK_ADJUSTMENT'
        THEN fact.LineAmount ELSE 0 END) AS OperationalAdjustmentLineAmount
FROM analytics.FactTransaction AS fact
INNER JOIN analytics.DimDate AS date_dimension
    ON date_dimension.DateKey = fact.DateKey
GROUP BY
    date_dimension.[Year],
    date_dimension.MonthNumber,
    date_dimension.YearMonth;
GO
