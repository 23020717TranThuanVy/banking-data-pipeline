"""Unit checks for SQL Server connection settings and load behavior."""

from datetime import datetime
from decimal import Decimal
from types import ModuleType

import pytest

from banking_pipeline.load import build_connection_string, load_transactions
from banking_pipeline.transform import Transaction


CONNECTION_SETTINGS = {
    "DB_SERVER": "localhost\\SQLEXPRESS",
    "DB_DATABASE": "BankingTransactions",
    "DB_DRIVER": "ODBC Driver 18 for SQL Server",
    "DB_TRUSTED_CONNECTION": "yes",
    "DB_ENCRYPT": "yes",
    "DB_TRUST_SERVER_CERTIFICATE": "yes",
}


def make_transaction(transaction_id: str) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        account_id="ACC1000",
        transaction_date=datetime(2026, 10, 1, 10, 0),
        transaction_type="deposit",
        amount=Decimal("100.00"),
        currency="VND",
        status="completed",
        counterparty_account_id=None,
    )


def test_connection_string_uses_environment_settings_without_credentials() -> None:
    connection_string = build_connection_string(CONNECTION_SETTINGS)

    assert "SERVER={localhost\\SQLEXPRESS}" in connection_string
    assert "DATABASE={BankingTransactions}" in connection_string
    assert "DRIVER={ODBC Driver 18 for SQL Server}" in connection_string
    assert "Trusted_Connection=yes" in connection_string
    assert "PWD=" not in connection_string


def test_connection_string_reports_missing_required_settings() -> None:
    with pytest.raises(ValueError, match="DB_SERVER"):
        build_connection_string({})


def test_loader_counts_new_and_existing_rows_and_commits_once(monkeypatch) -> None:
    class FakeCursor:
        def __init__(self) -> None:
            self.description = None
            self.flags = iter([1, 0])
            self.executed = []
            self.current_flag = None
            self.closed = False

        def execute(self, query, *parameters):
            self.executed.append((query, parameters))
            self.current_flag = next(self.flags)
            self.description = None
            return self

        def nextset(self):
            self.description = (("was_inserted",),)
            return True

        def fetchone(self):
            return (self.current_flag,)

        def close(self):
            self.closed = True

    class FakeConnection:
        def __init__(self) -> None:
            self.fake_cursor = FakeCursor()
            self.commits = 0
            self.rollbacks = 0
            self.closed = False

        def cursor(self):
            return self.fake_cursor

        def commit(self):
            self.commits += 1

        def rollback(self):
            self.rollbacks += 1

        def close(self):
            self.closed = True

    connection = FakeConnection()
    connect_calls = []
    fake_pyodbc = ModuleType("pyodbc")
    fake_pyodbc.connect = lambda value: connect_calls.append(value) or connection
    fake_dotenv = ModuleType("dotenv")
    fake_dotenv.load_dotenv = lambda *args, **kwargs: None
    monkeypatch.setitem(__import__("sys").modules, "pyodbc", fake_pyodbc)
    monkeypatch.setitem(__import__("sys").modules, "dotenv", fake_dotenv)
    for name, value in CONNECTION_SETTINGS.items():
        monkeypatch.setenv(name, value)

    result = load_transactions([make_transaction("TXN2001"), make_transaction("TXN2002")])

    assert result.inserted == 1
    assert result.skipped_existing == 1
    assert connection.commits == 1
    assert connection.rollbacks == 0
    assert connection.closed is True
    assert connection.fake_cursor.closed is True
    assert len(connect_calls) == 1
    assert len(connection.fake_cursor.executed) == 2
    for query, parameters in connection.fake_cursor.executed:
        assert "WITH (UPDLOCK, HOLDLOCK)" in query
        assert "VALUES (?, ?, ?, ?, ?, ?, ?, ?)" in query
        assert len(parameters) == 9
