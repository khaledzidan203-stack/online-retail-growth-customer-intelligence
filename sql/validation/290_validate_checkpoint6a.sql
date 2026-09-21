USE [OnlineRetailAnalytics];
GO

DECLARE @Validation TABLE
(
    Metric NVARCHAR(200) NOT NULL,
    Actual DECIMAL(38,8) NOT NULL,
    Expected DECIMAL(38,8) NOT NULL,
    Status VARCHAR(4) NOT NULL
);

INSERT INTO @Validation
SELECT N'CustomerRFM rows', COUNT_BIG(*), 5852,
    CASE WHEN COUNT_BIG(*) = 5852 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRFM;

INSERT INTO @Validation
SELECT N'CustomerCohort rows', COUNT_BIG(*), 5852,
    CASE WHEN COUNT_BIG(*) = 5852 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerCohort;

INSERT INTO @Validation
SELECT N'CustomerRepeatBehavior rows', COUNT_BIG(*), 5852,
    CASE WHEN COUNT_BIG(*) = 5852 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRepeatBehavior;

INSERT INTO @Validation
SELECT N'Customer360 rows', COUNT_BIG(*), 5852,
    CASE WHEN COUNT_BIG(*) = 5852 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.vw_Customer360;

INSERT INTO @Validation
SELECT N'CohortRetention rows', COUNT_BIG(*), 325,
    CASE WHEN COUNT_BIG(*) = 325 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CohortRetention;

INSERT INTO @Validation
SELECT N'CohortRevenue rows', COUNT_BIG(*), 325,
    CASE WHEN COUNT_BIG(*) = 325 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CohortRevenue;

INSERT INTO @Validation
SELECT N'RFM monetary total', SUM(Monetary), CAST(17125672.047 AS DECIMAL(38,8)),
    CASE WHEN SUM(Monetary) = CAST(17125672.047 AS DECIMAL(38,8)) THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRFM;

INSERT INTO @Validation
SELECT N'RFM frequency total', SUM(CONVERT(BIGINT, Frequency)), 36597,
    CASE WHEN SUM(CONVERT(BIGINT, Frequency)) = 36597 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRFM;

INSERT INTO @Validation
SELECT N'Segment customer total', COUNT_BIG(*), 5852,
    CASE WHEN COUNT_BIG(*) = 5852 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRFM WHERE Segment IS NOT NULL;

DECLARE @Segments TABLE (Segment NVARCHAR(50), ExpectedCount INT);
INSERT INTO @Segments VALUES
    (N'Champions', 1261),
    (N'Loyal Customers', 594),
    (N'Potential Loyalists', 716),
    (N'New Customers', 78),
    (N'Promising', 455),
    (N'Need Attention', 409),
    (N'At Risk', 709),
    (N'Hibernating', 681),
    (N'Lost', 949);

INSERT INTO @Validation
SELECT
    N'Segment: ' + expected.Segment,
    COUNT_BIG(actual.CustomerKey),
    expected.ExpectedCount,
    CASE WHEN COUNT_BIG(actual.CustomerKey) = expected.ExpectedCount
        THEN 'PASS' ELSE 'FAIL' END
FROM @Segments AS expected
LEFT JOIN analytics.CustomerRFM AS actual
    ON actual.Segment = expected.Segment
GROUP BY expected.Segment, expected.ExpectedCount;

INSERT INTO @Validation
SELECT N'Cohort size total', SUM(CONVERT(BIGINT, CohortSize)), 5852,
    CASE WHEN SUM(CONVERT(BIGINT, CohortSize)) = 5852 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CohortRetention WHERE CohortIndex = 0;

INSERT INTO @Validation
SELECT N'Repeat customers', COUNT_BIG(*), 4234,
    CASE WHEN COUNT_BIG(*) = 4234 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRepeatBehavior WHERE HasRepeatPurchase = 1;

INSERT INTO @Validation
SELECT N'Non-repeat customers', COUNT_BIG(*), 1618,
    CASE WHEN COUNT_BIG(*) = 1618 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRepeatBehavior WHERE HasRepeatPurchase = 0;

INSERT INTO @Validation
SELECT N'Month 0 invalid retention rows', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CohortRetention
WHERE CohortIndex = 0
  AND (ActiveCustomers <> CohortSize OR RetentionRate <> 1);

INSERT INTO @Validation
SELECT N'Customer table set mismatches', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM
(
    SELECT CustomerKey, CustomerID FROM
    (
        SELECT CustomerKey, CustomerID FROM analytics.CustomerRFM
        EXCEPT SELECT CustomerKey, CustomerID FROM analytics.CustomerCohort
    ) AS rfm_not_cohort
    UNION ALL
    SELECT CustomerKey, CustomerID FROM
    (
        SELECT CustomerKey, CustomerID FROM analytics.CustomerCohort
        EXCEPT SELECT CustomerKey, CustomerID FROM analytics.CustomerRepeatBehavior
    ) AS cohort_not_repeat
    UNION ALL
    SELECT CustomerKey, CustomerID FROM
    (
        SELECT CustomerKey, CustomerID FROM analytics.CustomerRepeatBehavior
        EXCEPT SELECT CustomerKey, CustomerID FROM analytics.CustomerRFM
    ) AS repeat_not_rfm
) AS mismatch;

INSERT INTO @Validation
SELECT N'Retention/revenue grain mismatches', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM
(
    SELECT AcquisitionCohort, CohortIndex FROM
    (
        SELECT AcquisitionCohort, CohortIndex FROM analytics.CohortRetention
        EXCEPT SELECT AcquisitionCohort, CohortIndex FROM analytics.CohortRevenue
    ) AS retention_not_revenue
    UNION ALL
    SELECT AcquisitionCohort, CohortIndex FROM
    (
        SELECT AcquisitionCohort, CohortIndex FROM analytics.CohortRevenue
        EXCEPT SELECT AcquisitionCohort, CohortIndex FROM analytics.CohortRetention
    ) AS revenue_not_retention
) AS mismatch;

INSERT INTO @Validation
SELECT N'Broken CustomerRFM customer keys', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRFM AS item
LEFT JOIN analytics.DimCustomer AS customer ON customer.CustomerKey = item.CustomerKey
WHERE customer.CustomerKey IS NULL;

INSERT INTO @Validation
SELECT N'Broken CustomerCohort customer keys', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerCohort AS item
LEFT JOIN analytics.DimCustomer AS customer ON customer.CustomerKey = item.CustomerKey
WHERE customer.CustomerKey IS NULL;

INSERT INTO @Validation
SELECT N'Broken CustomerRepeatBehavior customer keys', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRepeatBehavior AS item
LEFT JOIN analytics.DimCustomer AS customer ON customer.CustomerKey = item.CustomerKey
WHERE customer.CustomerKey IS NULL;

INSERT INTO @Validation
SELECT N'Duplicate or anonymous customer leakage', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM
(
    SELECT CustomerID FROM analytics.CustomerRFM
    WHERE CustomerID IS NULL OR LTRIM(RTRIM(CustomerID)) = ''
    UNION ALL
    SELECT CustomerID FROM analytics.CustomerCohort
    WHERE CustomerID IS NULL OR LTRIM(RTRIM(CustomerID)) = ''
    UNION ALL
    SELECT CustomerID FROM analytics.CustomerRepeatBehavior
    WHERE CustomerID IS NULL OR LTRIM(RTRIM(CustomerID)) = ''
) AS invalid_customer;

INSERT INTO @Validation
SELECT N'Duplicate CustomerRFM keys or IDs', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM
(
    SELECT N'KEY' AS DuplicateType FROM analytics.CustomerRFM
    GROUP BY CustomerKey HAVING COUNT_BIG(*) > 1
    UNION ALL
    SELECT N'ID' FROM analytics.CustomerRFM
    GROUP BY CustomerID HAVING COUNT_BIG(*) > 1
) AS duplicate_value;

INSERT INTO @Validation
SELECT N'Duplicate CustomerCohort keys or IDs', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM
(
    SELECT N'KEY' AS DuplicateType FROM analytics.CustomerCohort
    GROUP BY CustomerKey HAVING COUNT_BIG(*) > 1
    UNION ALL
    SELECT N'ID' FROM analytics.CustomerCohort
    GROUP BY CustomerID HAVING COUNT_BIG(*) > 1
) AS duplicate_value;

INSERT INTO @Validation
SELECT N'Duplicate CustomerRepeatBehavior keys or IDs', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM
(
    SELECT N'KEY' AS DuplicateType FROM analytics.CustomerRepeatBehavior
    GROUP BY CustomerKey HAVING COUNT_BIG(*) > 1
    UNION ALL
    SELECT N'ID' FROM analytics.CustomerRepeatBehavior
    GROUP BY CustomerID HAVING COUNT_BIG(*) > 1
) AS duplicate_value;

INSERT INTO @Validation
SELECT N'Unclassified RFM customers', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRFM
WHERE Segment NOT IN
(
    N'Champions', N'Loyal Customers', N'Potential Loyalists',
    N'New Customers', N'Promising', N'Need Attention', N'At Risk',
    N'Hibernating', N'Lost'
);

INSERT INTO @Validation
SELECT N'Customer360 duplicate keys or IDs', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM
(
    SELECT N'KEY' AS DuplicateType FROM analytics.vw_Customer360
    GROUP BY CustomerKey HAVING COUNT_BIG(*) > 1
    UNION ALL
    SELECT N'ID' FROM analytics.vw_Customer360
    GROUP BY CustomerID HAVING COUNT_BIG(*) > 1
) AS duplicate_value;

INSERT INTO @Validation
SELECT N'Incorrect RFM reference dates', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerRFM
WHERE ReferenceDate <> CONVERT(DATE, '2011-12-10');

INSERT INTO @Validation
SELECT N'Incorrect left-boundary cohort flags', COUNT_BIG(*), 0,
    CASE WHEN COUNT_BIG(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM analytics.CustomerCohort
WHERE (AcquisitionCohort = '2009-12' AND IsLeftBoundaryAffected <> 1)
   OR (AcquisitionCohort <> '2009-12' AND IsLeftBoundaryAffected <> 0);

SELECT Metric, Actual, Expected, Status
FROM @Validation
ORDER BY Metric;
GO
