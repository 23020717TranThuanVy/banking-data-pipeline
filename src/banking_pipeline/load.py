"""Load validated transactions into SQL Server Express without duplicates."""

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Iterable, Mapping

from .transform import Transaction


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INSERT_IF_MISSING_SQL = """
SET NOCOUNT ON;
IF EXISTS (
    SELECT 1
    FROM dbo.transactions WITH (UPDLOCK, HOLDLOCK)
    WHERE transaction_id = ?
)
BEGIN
    SELECT CAST(0 AS int) AS was_inserted;
END
ELSE
BEGIN
    INSERT INTO dbo.transactions (
        transaction_id, account_id, transaction_date, transaction_type,
        amount, currency, [status], counterparty_account_id
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    SELECT CAST(1 AS int) AS was_inserted;
END;
"""


@dataclass(frozen=True)
class LoadSummary:
    inserted: int
    skipped_existing: int


def _odbc_value(value: str) -> str:
    """Brace-quote an ODBC connection value and escape closing braces."""
    return "{" + value.replace("}", "}}") + "}"


def build_connection_string(env: Mapping[str, str] | None = None) -> str:
    """Build a connection string from environment variables, never literals."""
    settings = os.environ if env is None else env
    required = ("DB_SERVER", "DB_DATABASE", "DB_DRIVER")
    missing = [name for name in required if not settings.get(name)]
    if missing:
        raise ValueError("Missing database settings: " + ", ".join(missing))

    parts = [
        "DRIVER=" + _odbc_value(settings["DB_DRIVER"]),
        "SERVER=" + _odbc_value(settings["DB_SERVER"]),
        "DATABASE=" + _odbc_value(settings["DB_DATABASE"]),
    ]
    trusted = settings.get("DB_TRUSTED_CONNECTION", "yes").strip().lower()

    if trusted in {"yes", "true", "1"}:
        parts.append("Trusted_Connection=yes")
    else:
        username = settings.get("DB_USERNAME", "")
        password = settings.get("DB_PASSWORD", "")
        if not username or not password:
            raise ValueError(
                "Set DB_USERNAME and DB_PASSWORD when trusted connection is disabled."
            )
        parts.extend(
            ["UID=" + _odbc_value(username), "PWD=" + _odbc_value(password)]
        )

    encrypt = settings.get("DB_ENCRYPT", "yes").strip().lower()
    trust_certificate = settings.get(
        "DB_TRUST_SERVER_CERTIFICATE", "yes"
    ).strip().lower()
    parts.extend(
        [
            "Encrypt=" + ("yes" if encrypt in {"yes", "true", "1"} else "no"),
            "TrustServerCertificate="
            + ("yes" if trust_certificate in {"yes", "true", "1"} else "no"),
            "Connection Timeout=30",
        ]
    )
    return ";".join(parts) + ";"


def load_transactions(transactions: Iterable[Transaction]) -> LoadSummary:
    """Insert new transactions in one DB transaction and skip existing IDs.

    The destination table must already exist. Every SQL value is parameterized.
    A primary key plus SQL Server range locks protects the idempotency check.
    """
    try:
        import pyodbc
        from dotenv import load_dotenv
    except ImportError as error:
        raise RuntimeError(
            "Database loading needs pyodbc and python-dotenv. "
            "Install the project requirements in its virtual environment first."
        ) from error

    load_dotenv(PROJECT_ROOT / ".env")
    connection = pyodbc.connect(build_connection_string())
    cursor = connection.cursor()
    inserted = 0
    skipped_existing = 0

    try:
        for transaction in transactions:
            cursor.execute(
                INSERT_IF_MISSING_SQL,
                transaction.transaction_id,
                transaction.transaction_id,
                transaction.account_id,
                transaction.transaction_date,
                transaction.transaction_type,
                transaction.amount,
                transaction.currency,
                transaction.status,
                transaction.counterparty_account_id,
            )
            while cursor.description is None:
                if not cursor.nextset():
                    raise RuntimeError(
                        "SQL Server did not return the insert/skip result."
                    )
            was_inserted = cursor.fetchone()[0]
            if was_inserted:
                inserted += 1
            else:
                skipped_existing += 1
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

    return LoadSummary(inserted=inserted, skipped_existing=skipped_existing)
