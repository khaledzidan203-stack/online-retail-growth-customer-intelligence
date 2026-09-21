USE [master];
GO

IF DB_ID(N'OnlineRetailAnalytics') IS NULL
BEGIN
    CREATE DATABASE [OnlineRetailAnalytics];
END;
GO
