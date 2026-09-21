USE [OnlineRetailAnalytics];
GO

IF OBJECT_ID(N'raw.OnlineRetailTransaction', N'U') IS NULL
BEGIN
    CREATE TABLE raw.OnlineRetailTransaction
    (
        RawTransactionKey BIGINT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_raw_OnlineRetailTransaction PRIMARY KEY,
        SourceSheet NVARCHAR(50) NOT NULL,
        SourceRowNumber INT NOT NULL,
        InvoiceRaw NVARCHAR(100) NULL,
        Invoice NVARCHAR(100) NULL,
        StockCodeRaw NVARCHAR(100) NULL,
        StockCode NVARCHAR(100) NULL,
        DescriptionRaw NVARCHAR(1000) NULL,
        Description NVARCHAR(1000) NULL,
        Quantity INT NOT NULL,
        InvoiceDate DATETIME2(0) NOT NULL,
        Price DECIMAL(19,8) NOT NULL,
        CustomerIDRaw DECIMAL(19,4) NULL,
        CustomerID NVARCHAR(50) NULL,
        CountryRaw NVARCHAR(200) NULL,
        Country NVARCHAR(200) NULL,
        LineAmount DECIMAL(28,8) NOT NULL,
        IsExactDuplicateAfterFirst BIT NOT NULL,
        IsInExactDuplicateGroup BIT NOT NULL,
        ExactDuplicateGroupSize INT NOT NULL,
        ItemClass NVARCHAR(50) NOT NULL,
        TransactionClass NVARCHAR(50) NOT NULL,
        DQReviewReason NVARCHAR(500) NULL,
        IsKnownCustomer BIT NOT NULL,
        IsCancellationInvoice BIT NOT NULL,
        IsMerchandise BIT NOT NULL,
        IsSalesEligible BIT NOT NULL,
        IsCustomerAnalyticsEligible BIT NOT NULL,
        IsCancellationEligible BIT NOT NULL,
        IsZeroPrice BIT NOT NULL,
        IsNegativePrice BIT NOT NULL
    );
END;
GO
