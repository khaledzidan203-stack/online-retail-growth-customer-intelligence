USE [OnlineRetailAnalytics];
GO

IF OBJECT_ID(N'staging.TransactionCanonical', N'U') IS NULL
BEGIN
    CREATE TABLE staging.TransactionCanonical
    (
        TransactionLineKey BIGINT NOT NULL
            CONSTRAINT PK_staging_TransactionCanonical PRIMARY KEY,
        SourceSheet NVARCHAR(50) NOT NULL,
        SourceRowNumber INT NOT NULL,
        Invoice NVARCHAR(100) NULL,
        StockCode NVARCHAR(100) NULL,
        Description NVARCHAR(1000) NULL,
        Quantity INT NOT NULL,
        InvoiceDate DATETIME2(0) NOT NULL,
        Price DECIMAL(19,8) NOT NULL,
        CustomerID NVARCHAR(50) NULL,
        Country NVARCHAR(200) NULL,
        LineAmount DECIMAL(28,8) NOT NULL,
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
        IsNegativePrice BIT NOT NULL,
        IsExactDuplicateAfterFirst BIT NOT NULL,
        IsInExactDuplicateGroup BIT NOT NULL,
        ExactDuplicateGroupSize INT NOT NULL
    );
END;
GO

TRUNCATE TABLE staging.TransactionCanonical;

INSERT INTO staging.TransactionCanonical
(
    TransactionLineKey,
    SourceSheet,
    SourceRowNumber,
    Invoice,
    StockCode,
    Description,
    Quantity,
    InvoiceDate,
    Price,
    CustomerID,
    Country,
    LineAmount,
    ItemClass,
    TransactionClass,
    DQReviewReason,
    IsKnownCustomer,
    IsCancellationInvoice,
    IsMerchandise,
    IsSalesEligible,
    IsCustomerAnalyticsEligible,
    IsCancellationEligible,
    IsZeroPrice,
    IsNegativePrice,
    IsExactDuplicateAfterFirst,
    IsInExactDuplicateGroup,
    ExactDuplicateGroupSize
)
SELECT
    RawTransactionKey,
    SourceSheet,
    SourceRowNumber,
    Invoice,
    StockCode,
    Description,
    Quantity,
    InvoiceDate,
    Price,
    CustomerID,
    Country,
    LineAmount,
    ItemClass,
    TransactionClass,
    DQReviewReason,
    IsKnownCustomer,
    IsCancellationInvoice,
    IsMerchandise,
    IsSalesEligible,
    IsCustomerAnalyticsEligible,
    IsCancellationEligible,
    IsZeroPrice,
    IsNegativePrice,
    IsExactDuplicateAfterFirst,
    IsInExactDuplicateGroup,
    ExactDuplicateGroupSize
FROM raw.OnlineRetailTransaction;
GO
