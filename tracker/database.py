"""
database.py - SQLite storage for price check history.
"""
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "price_history.db"


@dataclass
class PriceCheck:
    id: int
    timestamp: str
    title: str
    price: float
    in_stock: bool
    stock_count: Optional[int]


@contextmanager
def get_connection(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path = DB_PATH) -> None:
    """Create the checks table if it doesn't already exist."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                in_stock INTEGER NOT NULL,
                stock_count INTEGER
            )
            """
        )
        conn.commit()


def save_check(
    title: str,
    price: float,
    in_stock: bool,
    stock_count: Optional[int],
    db_path: Path = DB_PATH,
) -> None:
    """Insert a new price check record."""
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO checks (timestamp, title, price, in_stock, stock_count) "
            "VALUES (?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), title, price, int(in_stock), stock_count),
        )
        conn.commit()


def get_latest_check(title: str, db_path: Path = DB_PATH) -> Optional[PriceCheck]:
    """Return the most recent check for a given product title, or None."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM checks WHERE title = ? ORDER BY id DESC LIMIT 1",
            (title,),
        ).fetchone()
        return PriceCheck(**dict(row)) if row else None


def get_history(title: str, db_path: Path = DB_PATH) -> list:
    """Return all checks for a given product, oldest first."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM checks WHERE title = ? ORDER BY id ASC",
            (title,),
        ).fetchall()
        return [PriceCheck(**dict(row)) for row in rows]
