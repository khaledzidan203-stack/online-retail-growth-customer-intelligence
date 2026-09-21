USE [OnlineRetailAnalytics];
GO

IF OBJECT_ID(N'analytics.CustomerRFM', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.CustomerRFM
    (
        CustomerKey INT NOT NULL CONSTRAINT PK_analytics_CustomerRFM PRIMARY KEY,
        CustomerID NVARCHAR(50) NOT NULL CONSTRAINT UQ_analytics_CustomerRFM_CustomerID UNIQUE,
        ReferenceDate DATE NOT NULL,
        Recency INT NOT NULL,
        Frequency INT NOT NULL,
        Monetary DECIMAL(28,8) NOT NULL,
        R_Score TINYINT NOT NULL,
        F_Score TINYINT NOT NULL,
        M_Score TINYINT NOT NULL,
        RFM_Code CHAR(3) NOT NULL,
        RFM_Total TINYINT NOT NULL,
        Segment NVARCHAR(50) NOT NULL,
        FirstPurchaseDate DATETIME2(0) NOT NULL,
        LastPurchaseDate DATETIME2(0) NOT NULL,
        UnitsPurchased BIGINT NOT NULL,
        ActiveLifespanDays INT NOT NULL,
        AverageOrderValue DECIMAL(28,8) NOT NULL,
        CONSTRAINT CK_CustomerRFM_RScore CHECK (R_Score BETWEEN 1 AND 5),
        CONSTRAINT CK_CustomerRFM_FScore CHECK (F_Score BETWEEN 1 AND 5),
        CONSTRAINT CK_CustomerRFM_MScore CHECK (M_Score BETWEEN 1 AND 5),
        CONSTRAINT FK_CustomerRFM_DimCustomer FOREIGN KEY (CustomerKey)
            REFERENCES analytics.DimCustomer (CustomerKey)
    );
END;
GO

IF OBJECT_ID(N'analytics.CustomerCohort', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.CustomerCohort
    (
        CustomerKey INT NOT NULL CONSTRAINT PK_analytics_CustomerCohort PRIMARY KEY,
        CustomerID NVARCHAR(50) NOT NULL CONSTRAINT UQ_analytics_CustomerCohort_CustomerID UNIQUE,
        FirstPurchaseDate DATETIME2(0) NOT NULL,
        AcquisitionCohort CHAR(7) NOT NULL,
        IsLeftBoundaryAffected BIT NOT NULL,
        CONSTRAINT CK_CustomerCohort_AcquisitionCohort
            CHECK (AcquisitionCohort LIKE '[12][0-9][0-9][0-9]-[01][0-9]'),
        CONSTRAINT FK_CustomerCohort_DimCustomer FOREIGN KEY (CustomerKey)
            REFERENCES analytics.DimCustomer (CustomerKey)
    );
END;
GO

IF OBJECT_ID(N'analytics.CohortRetention', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.CohortRetention
    (
        AcquisitionCohort CHAR(7) NOT NULL,
        CohortIndex INT NOT NULL,
        ActivityMonth CHAR(7) NOT NULL,
        CohortSize INT NOT NULL,
        ActiveCustomers INT NOT NULL,
        RetentionRate DECIMAL(19,12) NOT NULL,
        IsLeftBoundaryCohort BIT NOT NULL,
        IsPartialObservation BIT NOT NULL,
        ObservationStatus NVARCHAR(40) NOT NULL,
        CONSTRAINT PK_analytics_CohortRetention
            PRIMARY KEY (AcquisitionCohort, CohortIndex),
        CONSTRAINT CK_CohortRetention_Index CHECK (CohortIndex >= 0),
        CONSTRAINT CK_CohortRetention_Rate CHECK (RetentionRate BETWEEN 0 AND 1),
        CONSTRAINT CK_CohortRetention_Customers
            CHECK (ActiveCustomers BETWEEN 0 AND CohortSize)
    );
END;
GO

IF OBJECT_ID(N'analytics.CohortRevenue', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.CohortRevenue
    (
        AcquisitionCohort CHAR(7) NOT NULL,
        CohortIndex INT NOT NULL,
        ActivityMonth CHAR(7) NOT NULL,
        CohortSize INT NOT NULL,
        Revenue DECIMAL(28,8) NOT NULL,
        RevenuePerOriginalCustomer DECIMAL(28,8) NOT NULL,
        Orders INT NOT NULL,
        OrdersPerOriginalCustomer DECIMAL(19,12) NOT NULL,
        IsLeftBoundaryCohort BIT NOT NULL,
        IsPartialObservation BIT NOT NULL,
        ObservationStatus NVARCHAR(40) NOT NULL,
        CONSTRAINT PK_analytics_CohortRevenue
            PRIMARY KEY (AcquisitionCohort, CohortIndex),
        CONSTRAINT CK_CohortRevenue_Index CHECK (CohortIndex >= 0)
    );
END;
GO

IF OBJECT_ID(N'analytics.CustomerRepeatBehavior', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.CustomerRepeatBehavior
    (
        CustomerKey INT NOT NULL
            CONSTRAINT PK_analytics_CustomerRepeatBehavior PRIMARY KEY,
        CustomerID NVARCHAR(50) NOT NULL
            CONSTRAINT UQ_analytics_CustomerRepeatBehavior_CustomerID UNIQUE,
        FirstPurchaseDate DATETIME2(0) NOT NULL,
        SecondPurchaseDate DATETIME2(0) NULL,
        DaysToSecondPurchase INT NULL,
        HasRepeatPurchase BIT NOT NULL,
        CONSTRAINT CK_CustomerRepeatBehavior_SecondPurchase
            CHECK
            (
                (HasRepeatPurchase = 1 AND SecondPurchaseDate IS NOT NULL
                    AND DaysToSecondPurchase IS NOT NULL)
                OR
                (HasRepeatPurchase = 0 AND SecondPurchaseDate IS NULL
                    AND DaysToSecondPurchase IS NULL)
            ),
        CONSTRAINT FK_CustomerRepeatBehavior_DimCustomer FOREIGN KEY (CustomerKey)
            REFERENCES analytics.DimCustomer (CustomerKey)
    );
END;
GO

CREATE OR ALTER VIEW analytics.vw_Customer360
AS
SELECT
    customer.CustomerKey,
    customer.CustomerID,
    rfm.ReferenceDate,
    rfm.Recency,
    rfm.Frequency,
    rfm.Monetary,
    rfm.R_Score,
    rfm.F_Score,
    rfm.M_Score,
    rfm.RFM_Code,
    rfm.RFM_Total,
    rfm.Segment,
    rfm.FirstPurchaseDate,
    rfm.LastPurchaseDate,
    rfm.UnitsPurchased,
    rfm.ActiveLifespanDays,
    rfm.AverageOrderValue,
    cohort.AcquisitionCohort,
    cohort.IsLeftBoundaryAffected,
    repeat.HasRepeatPurchase,
    repeat.SecondPurchaseDate,
    repeat.DaysToSecondPurchase
FROM analytics.DimCustomer AS customer
INNER JOIN analytics.CustomerRFM AS rfm
    ON rfm.CustomerKey = customer.CustomerKey
INNER JOIN analytics.CustomerCohort AS cohort
    ON cohort.CustomerKey = customer.CustomerKey
INNER JOIN analytics.CustomerRepeatBehavior AS repeat
    ON repeat.CustomerKey = customer.CustomerKey;
GO

