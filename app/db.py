import os
import sqlite3
from typing import Tuple

DB_PATH = "inventory.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            name TEXT,
            quantity INTEGER,
            price_per_kg REAL,
            total_price REAL,
            category TEXT
        )
        """
    )

    # Add new columns if they do not exist (SQLite has no IF NOT EXISTS for columns)
    cursor.execute("PRAGMA table_info(inventory)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    if "sold_quantity" not in existing_cols:
        cursor.execute("ALTER TABLE inventory ADD COLUMN sold_quantity INTEGER DEFAULT 0")

    if "sold_total_cost" not in existing_cols:
        cursor.execute("ALTER TABLE inventory ADD COLUMN sold_total_cost REAL DEFAULT 0.0")

    # Ensure sold_total_cost is consistent for existing rows
    cursor.execute(
        """
        UPDATE inventory
        SET sold_total_cost = COALESCE(sold_quantity, 0) * COALESCE(price_per_kg, 0)
        """
    )
    conn.commit()
    conn.close()


