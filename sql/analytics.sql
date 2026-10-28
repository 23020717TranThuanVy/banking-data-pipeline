/*
Run these queries against the project database.
Each SELECT is independent and returns one result set.
*/
USE [BankingTransactions];
GO

-- 1. Transaction count and gross transaction amount by day.
-- The amount is a positive transaction volume, not a net account balance.
SELECT
    CONVERT(date, transaction_date) AS transaction_day,
    COUNT_BIG(*) AS transaction_count,
    SUM(amount) AS total_transaction_amount,
    AVG(amount) AS average_transaction_amount
FROM dbo.transactions
GROUP BY CONVERT(date, transaction_date)
ORDER BY transaction_day;

-- 2. Transaction count and gross amount by transaction type.
SELECT
    transaction_type,
    COUNT_BIG(*) AS transaction_count,
    SUM(amount) AS total_transaction_amount
FROM dbo.transactions
GROUP BY transaction_type
ORDER BY total_transaction_amount DESC;

-- 3. Transaction count and gross amount by processing status.
SELECT
    [status],
    COUNT_BIG(*) AS transaction_count,
    SUM(amount) AS total_transaction_amount
FROM dbo.transactions
GROUP BY [status]
ORDER BY [status];

-- 4. Top source accounts by transaction count and gross amount.
-- This groups by account_id only; counterparty accounts are not included.
SELECT TOP (10)
    account_id,
    COUNT_BIG(*) AS transaction_count,
    SUM(amount) AS total_transaction_amount
FROM dbo.transactions
GROUP BY account_id
ORDER BY total_transaction_amount DESC, account_id;

-- 5. Inspect failed transactions.
SELECT
    transaction_id,
    account_id,
    transaction_date,
    transaction_type,
    amount,
    currency,
    [status],
    counterparty_account_id
FROM dbo.transactions
WHERE [status] = 'failed'
ORDER BY transaction_date;
