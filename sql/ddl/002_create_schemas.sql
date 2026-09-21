USE [OnlineRetailAnalytics];
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'raw')
    EXEC(N'CREATE SCHEMA [raw] AUTHORIZATION [dbo];');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'staging')
    EXEC(N'CREATE SCHEMA [staging] AUTHORIZATION [dbo];');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'analytics')
    EXEC(N'CREATE SCHEMA [analytics] AUTHORIZATION [dbo];');
GO
