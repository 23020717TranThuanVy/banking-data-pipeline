# SQL scripts

- `schema.sql` creates `dbo.transactions` in the database selected in the SQL client. It does not create a database or change server configuration.
- `transactions` uses `transaction_id` as its primary key and has checks for positive amounts, known transaction types, statuses, and a three-letter currency code.
- `src/banking_pipeline/load.py` uses parameterized SQL and skips transaction IDs already stored, so running the same load again does not insert duplicates.

See `docs/quality_rules.md` for the Python-side validation rules. The SQL Server loader has not been run yet.
