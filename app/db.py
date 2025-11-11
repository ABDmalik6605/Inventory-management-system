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
    
    # Create purchases/receipts table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            product_name TEXT,
            quantity INTEGER,
            selling_price_per_unit REAL,
            stock_price_per_unit REAL,
            total_selling_price REAL,
            total_stock_cost REAL,
            profit REAL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # MIGRATION: older schema incorrectly had UNIQUE(invoice_number) which
    # prevents multi-line invoices. If detected, recreate table without UNIQUE.
    try:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='purchases'")
        row = cursor.fetchone()
        if row and row[0]:
            sql_def = row[0].upper()
            # Check if UNIQUE constraint exists on invoice_number
            if "UNIQUE" in sql_def and "INVOICE_NUMBER" in sql_def:
                # Save existing data first
                cursor.execute("SELECT * FROM purchases")
                existing_data = cursor.fetchall()
                
                # Drop old table
                cursor.execute("DROP TABLE purchases")
                
                # Create new table WITHOUT UNIQUE constraint
                cursor.execute(
                    """
                    CREATE TABLE purchases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_number TEXT,
                        product_name TEXT,
                        quantity INTEGER,
                        selling_price_per_unit REAL,
                        stock_price_per_unit REAL,
                        total_selling_price REAL,
                        total_stock_cost REAL,
                        profit REAL,
                        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                
                # Restore data if any
                if existing_data:
                    for row_data in existing_data:
                        cursor.execute(
                            """
                            INSERT INTO purchases (
                                invoice_number, product_name, quantity, selling_price_per_unit,
                                stock_price_per_unit, total_selling_price, total_stock_cost, 
                                profit, purchase_date
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (row_data[1], row_data[2], row_data[3], row_data[4], 
                             row_data[5], row_data[6], row_data[7], row_data[8], row_data[9] if len(row_data) > 9 else None)
                        )
    except Exception as e:
        # Log error but continue - receipt_repository will handle it
        print(f"Migration warning: {e}")
    
    # Create receipt_items table for multi-item receipts
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS receipt_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            price_per_unit REAL,
            total_price REAL,
            FOREIGN KEY (invoice_number) REFERENCES receipts(invoice_number)
        )
        """
    )
    
    # Create receipts table for receipt metadata
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS receipts (
            invoice_number TEXT PRIMARY KEY,
            total_amount REAL,
            tax_amount REAL,
            grand_total REAL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            customer_name TEXT
        )
        """
    )
    
    conn.commit()
    conn.close()


