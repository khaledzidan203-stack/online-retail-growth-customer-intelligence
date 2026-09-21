USE [OnlineRetailAnalytics];
GO

IF OBJECT_ID(N'analytics.DimDate', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.DimDate
    (
        DateKey INT NOT NULL CONSTRAINT PK_analytics_DimDate PRIMARY KEY,
        FullDate DATE NOT NULL CONSTRAINT UQ_analytics_DimDate_FullDate UNIQUE,
        [Year] SMALLINT NOT NULL,
        [Quarter] TINYINT NOT NULL,
        MonthNumber TINYINT NOT NULL,
        MonthName NVARCHAR(20) NOT NULL,
        YearMonth CHAR(7) NOT NULL,
        WeekOfYear TINYINT NOT NULL,
        DayOfMonth TINYINT NOT NULL,
        DayName NVARCHAR(20) NOT NULL,
        DayOfWeekNumber TINYINT NOT NULL
    );
END;

IF OBJECT_ID(N'analytics.DimCustomer', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.DimCustomer
    (
        CustomerKey INT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_analytics_DimCustomer PRIMARY KEY,
        CustomerID NVARCHAR(50) NOT NULL
            CONSTRAINT UQ_analytics_DimCustomer_CustomerID UNIQUE
    );
END;

IF OBJECT_ID(N'analytics.DimProduct', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.DimProduct
    (
        ProductKey INT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_analytics_DimProduct PRIMARY KEY,
        StockCode NVARCHAR(100) NOT NULL
            CONSTRAINT UQ_analytics_DimProduct_StockCode UNIQUE,
        RepresentativeDescription NVARCHAR(1000) NULL,
        ItemClass NVARCHAR(50) NOT NULL
    );
END;

IF OBJECT_ID(N'analytics.DimCountry', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.DimCountry
    (
        CountryKey INT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_analytics_DimCountry PRIMARY KEY,
        Country NVARCHAR(200) NOT NULL
            CONSTRAINT UQ_analytics_DimCountry_Country UNIQUE
    );
END;
GO

IF OBJECT_ID(N'analytics.FactTransaction', N'U') IS NOT NULL
    DELETE FROM analytics.FactTransaction;

IF OBJECT_ID(N'analytics.CustomerRFM', N'U') IS NOT NULL
    DELETE FROM analytics.CustomerRFM;
IF OBJECT_ID(N'analytics.CustomerCohort', N'U') IS NOT NULL
    DELETE FROM analytics.CustomerCohort;
IF OBJECT_ID(N'analytics.CustomerRepeatBehavior', N'U') IS NOT NULL
    DELETE FROM analytics.CustomerRepeatBehavior;
IF OBJECT_ID(N'analytics.CohortRetention', N'U') IS NOT NULL
    DELETE FROM analytics.CohortRetention;
IF OBJECT_ID(N'analytics.CohortRevenue', N'U') IS NOT NULL
    DELETE FROM analytics.CohortRevenue;

DELETE FROM analytics.DimDate;
DELETE FROM analytics.DimCustomer;
DELETE FROM analytics.DimProduct;
DELETE FROM analytics.DimCountry;
GO

DECLARE @StartDate DATE =
(
    SELECT MIN(CONVERT(DATE, InvoiceDate))
    FROM staging.TransactionCanonical
);
DECLARE @EndDate DATE =
(
    SELECT MAX(CONVERT(DATE, InvoiceDate))
    FROM staging.TransactionCanonical
);

WITH CalendarDates AS
(
    SELECT @StartDate AS FullDate
    UNION ALL
    SELECT DATEADD(DAY, 1, FullDate)
    FROM CalendarDates
    WHERE FullDate < @EndDate
)
INSERT INTO analytics.DimDate
(
    DateKey,
    FullDate,
    [Year],
    [Quarter],
    MonthNumber,
    MonthName,
    YearMonth,
    WeekOfYear,
    DayOfMonth,
    DayName,
    DayOfWeekNumber
)
SELECT
    CONVERT(INT, CONVERT(CHAR(8), FullDate, 112)),
    FullDate,
    DATEPART(YEAR, FullDate),
    DATEPART(QUARTER, FullDate),
    DATEPART(MONTH, FullDate),
    DATENAME(MONTH, FullDate),
    CONVERT(CHAR(7), FullDate, 126),
    DATEPART(ISO_WEEK, FullDate),
    DATEPART(DAY, FullDate),
    DATENAME(WEEKDAY, FullDate),
    CONVERT(TINYINT, ((DATEDIFF(DAY, '19000101', FullDate) % 7) + 1))
FROM CalendarDates
OPTION (MAXRECURSION 0);
GO

INSERT INTO analytics.DimCustomer (CustomerID)
SELECT DISTINCT CustomerID
FROM staging.TransactionCanonical
WHERE CustomerID IS NOT NULL;
GO

WITH DescriptionFrequency AS
(
    SELECT
        StockCode,
        Description,
        COUNT_BIG(*) AS Occurrences
    FROM staging.TransactionCanonical
    WHERE StockCode IS NOT NULL
      AND Description IS NOT NULL
    GROUP BY StockCode, Description
),
RankedDescriptions AS
(
    SELECT
        StockCode,
        Description,
        ROW_NUMBER() OVER
        (
            PARTITION BY StockCode
            ORDER BY Occurrences DESC, Description ASC
        ) AS DescriptionRank
    FROM DescriptionFrequency
),
ProductCodes AS
(
    SELECT
        StockCode,
        MAX(ItemClass) AS ItemClass
    FROM staging.TransactionCanonical
    WHERE StockCode IS NOT NULL
    GROUP BY StockCode
)
INSERT INTO analytics.DimProduct
(
    StockCode,
    RepresentativeDescription,
    ItemClass
)
SELECT
    product.StockCode,
    description_choice.Description,
    product.ItemClass
FROM ProductCodes AS product
LEFT JOIN RankedDescriptions AS description_choice
    ON description_choice.StockCode = product.StockCode
   AND description_choice.DescriptionRank = 1;
GO

INSERT INTO analytics.DimCountry (Country)
SELECT DISTINCT Country
FROM staging.TransactionCanonical
WHERE Country IS NOT NULL;
GO
