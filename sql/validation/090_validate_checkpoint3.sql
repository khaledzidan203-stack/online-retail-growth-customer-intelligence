USE [OnlineRetailAnalytics];
GO

SET NOCOUNT ON;

DECLARE @Results TABLE
(
    SortOrder INT NOT NULL,
    Metric NVARCHAR(200) NOT NULL,
    ActualValue DECIMAL(38,8) NOT NULL,
    ExpectedValue DECIMAL(38,8) NULL
);

INSERT INTO @Results VALUES
(10, N'Raw rows',
    (SELECT COUNT_BIG(*) FROM raw.OnlineRetailTransaction), 1044848),
(20, N'Staging rows',
    (SELECT COUNT_BIG(*) FROM staging.TransactionCanonical), 1044848),
(30, N'FactTransaction rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction), 1044848),
(40, N'DimCustomer rows',
    (SELECT COUNT_BIG(*) FROM analytics.DimCustomer), 5942),
(50, N'DimCountry rows',
    (SELECT COUNT_BIG(*) FROM analytics.DimCountry), 43),
(60, N'DimProduct rows',
    (SELECT COUNT_BIG(*) FROM analytics.DimProduct),
    (SELECT COUNT_BIG(*) FROM
        (SELECT DISTINCT StockCode
         FROM staging.TransactionCanonical) AS governed_products)),
(65, N'Governed StockCodes vs Checkpoint 1 trimmed baseline',
    (SELECT COUNT_BIG(*) FROM
        (SELECT DISTINCT StockCode
         FROM staging.TransactionCanonical) AS governed_products), 5304),
(70, N'DimDate rows',
    (SELECT COUNT_BIG(*) FROM analytics.DimDate),
    (
        SELECT DATEDIFF
        (
            DAY,
            MIN(CONVERT(DATE, InvoiceDate)),
            MAX(CONVERT(DATE, InvoiceDate))
        ) + 1
        FROM staging.TransactionCanonical
    )),
(100, N'MERCHANDISE_SALE rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE TransactionClass = N'MERCHANDISE_SALE'), 1015091),
(110, N'CUSTOMER_CANCELLATION rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE TransactionClass = N'CUSTOMER_CANCELLATION'), 17974),
(120, N'NON_MERCHANDISE rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE TransactionClass = N'NON_MERCHANDISE'), 5719),
(130, N'OPERATIONAL_STOCK_ADJUSTMENT rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE TransactionClass = N'OPERATIONAL_STOCK_ADJUSTMENT'), 3392),
(140, N'ZERO_PRICE_MERCHANDISE rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE TransactionClass = N'ZERO_PRICE_MERCHANDISE'), 2582),
(150, N'ACCOUNTING_ADJUSTMENT rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE TransactionClass = N'ACCOUNTING_ADJUSTMENT'), 73),
(160, N'TEST_RECORD rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE TransactionClass = N'TEST_RECORD'), 17),
(170, N'DQ_REVIEW rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE TransactionClass = N'DQ_REVIEW'), 0),
(200, N'MERCHANDISE_SALE LineAmount',
    (SELECT COALESCE(SUM(LineAmount), 0) FROM analytics.FactTransaction
     WHERE TransactionClass = N'MERCHANDISE_SALE'), 19701685.507),
(210, N'CUSTOMER_CANCELLATION absolute LineAmount',
    (SELECT COALESCE(SUM(ABS(LineAmount)), 0) FROM analytics.FactTransaction
     WHERE TransactionClass = N'CUSTOMER_CANCELLATION'), 719692.94),
(220, N'Known-customer rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE IsKnownCustomer = 1), 809561),
(230, N'Unknown-customer rows',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE IsKnownCustomer = 0), 235287),
(240, N'Duplicate-extra flags',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE IsExactDuplicateAfterFirst = 1), 11812),
(250, N'Eligible merchandise-sale distinct invoices',
    (SELECT COUNT(DISTINCT Invoice) FROM analytics.FactTransaction
     WHERE IsSalesEligible = 1), 39519),
(260, N'Known distinct Customer IDs',
    (SELECT COUNT_BIG(*) FROM analytics.DimCustomer), 5942),
(300, N'Broken Date relationships',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction AS fact
     LEFT JOIN analytics.DimDate AS dimension
       ON dimension.DateKey = fact.DateKey
     WHERE dimension.DateKey IS NULL), 0),
(310, N'Broken Product relationships',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction AS fact
     LEFT JOIN analytics.DimProduct AS dimension
       ON dimension.ProductKey = fact.ProductKey
     WHERE dimension.ProductKey IS NULL), 0),
(320, N'Broken Country relationships',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction AS fact
     LEFT JOIN analytics.DimCountry AS dimension
       ON dimension.CountryKey = fact.CountryKey
     WHERE dimension.CountryKey IS NULL), 0),
(330, N'Known customers with null CustomerKey',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE IsKnownCustomer = 1 AND CustomerKey IS NULL), 0),
(340, N'Unknown customers with populated CustomerKey',
    (SELECT COUNT_BIG(*) FROM analytics.FactTransaction
     WHERE IsKnownCustomer = 0 AND CustomerKey IS NOT NULL), 0),
(350, N'Duplicate DimDate business keys',
    (SELECT COUNT_BIG(*) FROM
        (SELECT FullDate FROM analytics.DimDate
         GROUP BY FullDate HAVING COUNT_BIG(*) > 1) AS duplicates), 0),
(360, N'Duplicate DimCustomer business keys',
    (SELECT COUNT_BIG(*) FROM
        (SELECT CustomerID FROM analytics.DimCustomer
         GROUP BY CustomerID HAVING COUNT_BIG(*) > 1) AS duplicates), 0),
(370, N'Duplicate DimProduct business keys',
    (SELECT COUNT_BIG(*) FROM
        (SELECT StockCode FROM analytics.DimProduct
         GROUP BY StockCode HAVING COUNT_BIG(*) > 1) AS duplicates), 0),
(380, N'Duplicate DimCountry business keys',
    (SELECT COUNT_BIG(*) FROM
        (SELECT Country FROM analytics.DimCountry
         GROUP BY Country HAVING COUNT_BIG(*) > 1) AS duplicates), 0),
(390, N'Staging rows missing from fact',
    (SELECT COUNT_BIG(*) FROM staging.TransactionCanonical AS source
     LEFT JOIN analytics.FactTransaction AS fact
       ON fact.TransactionLineKey = source.TransactionLineKey
     WHERE fact.TransactionLineKey IS NULL), 0),
(400, N'Fact rows after dimension joins',
    (SELECT COUNT_BIG(*)
     FROM analytics.FactTransaction AS fact
     INNER JOIN analytics.DimDate AS date_dimension
       ON date_dimension.DateKey = fact.DateKey
     INNER JOIN analytics.DimProduct AS product
       ON product.ProductKey = fact.ProductKey
     INNER JOIN analytics.DimCountry AS country
       ON country.CountryKey = fact.CountryKey
     LEFT JOIN analytics.DimCustomer AS customer
       ON customer.CustomerKey = fact.CustomerKey), 1044848),
(410, N'StockCodes with inconsistent ItemClass',
    (SELECT COUNT_BIG(*) FROM
        (SELECT StockCode
         FROM staging.TransactionCanonical
         GROUP BY StockCode
         HAVING COUNT(DISTINCT ItemClass) > 1) AS inconsistent), 0),
(420, N'Representative product-description mismatches',
    (SELECT COUNT_BIG(*)
     FROM analytics.DimProduct AS product
     LEFT JOIN
     (
         SELECT StockCode, Description
         FROM
         (
             SELECT
                 StockCode,
                 Description,
                 ROW_NUMBER() OVER
                 (
                     PARTITION BY StockCode
                     ORDER BY COUNT_BIG(*) DESC, Description ASC
                 ) AS DescriptionRank
             FROM staging.TransactionCanonical
             WHERE Description IS NOT NULL
             GROUP BY StockCode, Description
         ) AS ranked
         WHERE DescriptionRank = 1
     ) AS expected_description
       ON expected_description.StockCode = product.StockCode
     WHERE
         product.RepresentativeDescription <> expected_description.Description
         OR
         (
             product.RepresentativeDescription IS NULL
             AND expected_description.Description IS NOT NULL
         )
         OR
         (
             product.RepresentativeDescription IS NOT NULL
             AND expected_description.Description IS NULL
         )), 0),
(900, N'StockCodes with multiple normalized descriptions',
    (SELECT COUNT_BIG(*) FROM
        (SELECT StockCode
         FROM staging.TransactionCanonical
         WHERE Description IS NOT NULL
         GROUP BY StockCode
         HAVING COUNT(DISTINCT Description) > 1) AS inconsistent), NULL);

SELECT
    Metric,
    ActualValue,
    ExpectedValue,
    CASE
        WHEN ExpectedValue IS NULL
          OR Metric = N'Governed StockCodes vs Checkpoint 1 trimmed baseline'
            THEN N'REVIEW'
        WHEN ActualValue = ExpectedValue THEN N'PASS'
        ELSE N'FAIL'
    END AS ValidationStatus
FROM @Results
ORDER BY SortOrder;
GO
