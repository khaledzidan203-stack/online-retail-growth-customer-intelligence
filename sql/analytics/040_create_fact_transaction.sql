USE [OnlineRetailAnalytics];
GO

IF OBJECT_ID(N'analytics.FactTransaction', N'U') IS NULL
BEGIN
    CREATE TABLE analytics.FactTransaction
    (
        TransactionLineKey BIGINT NOT NULL
            CONSTRAINT PK_analytics_FactTransaction PRIMARY KEY,
        DateKey INT NOT NULL,
        CustomerKey INT NULL,
        ProductKey INT NOT NULL,
        CountryKey INT NOT NULL,
        SourceSheet NVARCHAR(50) NOT NULL,
        SourceRowNumber INT NOT NULL,
        Invoice NVARCHAR(100) NULL,
        InvoiceDate DATETIME2(0) NOT NULL,
        LineDescription NVARCHAR(1000) NULL,
        Quantity INT NOT NULL,
        Price DECIMAL(19,8) NOT NULL,
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
        ExactDuplicateGroupSize INT NOT NULL,
        CONSTRAINT FK_FactTransaction_DimDate
            FOREIGN KEY (DateKey) REFERENCES analytics.DimDate (DateKey),
        CONSTRAINT FK_FactTransaction_DimCustomer
            FOREIGN KEY (CustomerKey) REFERENCES analytics.DimCustomer (CustomerKey),
        CONSTRAINT FK_FactTransaction_DimProduct
            FOREIGN KEY (ProductKey) REFERENCES analytics.DimProduct (ProductKey),
        CONSTRAINT FK_FactTransaction_DimCountry
            FOREIGN KEY (CountryKey) REFERENCES analytics.DimCountry (CountryKey)
    );
END;
GO

INSERT INTO analytics.FactTransaction
(
    TransactionLineKey,
    DateKey,
    CustomerKey,
    ProductKey,
    CountryKey,
    SourceSheet,
    SourceRowNumber,
    Invoice,
    InvoiceDate,
    LineDescription,
    Quantity,
    Price,
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
    source.TransactionLineKey,
    date_dimension.DateKey,
    customer.CustomerKey,
    product.ProductKey,
    country.CountryKey,
    source.SourceSheet,
    source.SourceRowNumber,
    source.Invoice,
    source.InvoiceDate,
    source.Description,
    source.Quantity,
    source.Price,
    source.LineAmount,
    source.ItemClass,
    source.TransactionClass,
    source.DQReviewReason,
    source.IsKnownCustomer,
    source.IsCancellationInvoice,
    source.IsMerchandise,
    source.IsSalesEligible,
    source.IsCustomerAnalyticsEligible,
    source.IsCancellationEligible,
    source.IsZeroPrice,
    source.IsNegativePrice,
    source.IsExactDuplicateAfterFirst,
    source.IsInExactDuplicateGroup,
    source.ExactDuplicateGroupSize
FROM staging.TransactionCanonical AS source
LEFT JOIN analytics.DimDate AS date_dimension
    ON date_dimension.FullDate = CONVERT(DATE, source.InvoiceDate)
LEFT JOIN analytics.DimCustomer AS customer
    ON customer.CustomerID = source.CustomerID
LEFT JOIN analytics.DimProduct AS product
    ON product.StockCode = source.StockCode
LEFT JOIN analytics.DimCountry AS country
    ON country.Country = source.Country;
GO
