-- Run this script in the target database. It creates the table only;
-- it does not create a database or change server configuration.
IF OBJECT_ID(N'dbo.transactions', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.transactions (
        transaction_id NVARCHAR(50) NOT NULL,
        account_id NVARCHAR(50) NOT NULL,
        transaction_date DATETIME2(0) NOT NULL,
        transaction_type VARCHAR(20) NOT NULL,
        amount DECIMAL(19, 4) NOT NULL,
        currency CHAR(3) NOT NULL,
        [status] VARCHAR(20) NOT NULL,
        counterparty_account_id NVARCHAR(50) NULL,
        loaded_at_utc DATETIME2(0) NOT NULL
            CONSTRAINT DF_transactions_loaded_at_utc DEFAULT SYSUTCDATETIME(),
        CONSTRAINT PK_transactions PRIMARY KEY (transaction_id),
        CONSTRAINT CK_transactions_amount_positive CHECK (amount > 0),
        CONSTRAINT CK_transactions_type CHECK (
            transaction_type IN ('deposit', 'withdrawal', 'transfer', 'payment')
        ),
        CONSTRAINT CK_transactions_status CHECK (
            [status] IN ('completed', 'pending', 'failed')
        ),
        CONSTRAINT CK_transactions_currency CHECK (
            currency NOT LIKE '%[^A-Z]%'
        )
    );
END;
GO
