from typing import List, Optional, Tuple
import sqlite3

from .db import get_connection


class InventoryRepository:
    def add_or_update(self, name: str, quantity: int, price_per_unit: float, category: str) -> None:
        name_normalized = name.strip().lower()
        category_normalized = category.strip().lower()

        conn = get_connection()
        cursor = conn.cursor()

        # If same name but different price exists, block
        cursor.execute(
            """
            SELECT id, quantity, price_per_kg FROM inventory
            WHERE LOWER(name) = ? AND price_per_kg != ?
            """,
            (name_normalized, price_per_unit),
        )
        conflict = cursor.fetchone()
        if conflict:
            conn.close()
            raise ValueError("PRICE_CONFLICT")

        # Same name and same price: update quantity
        cursor.execute(
            """
            SELECT id, quantity FROM inventory
            WHERE LOWER(name) = ? AND price_per_kg = ?
            """,
            (name_normalized, price_per_unit),
        )
        existing = cursor.fetchone()

        if existing:
            item_id, existing_qty = existing
            new_qty = existing_qty + quantity
            total_price = new_qty * price_per_unit
            cursor.execute(
                """
                UPDATE inventory
                SET quantity = ?, total_price = ?
                WHERE id = ?
                """,
                (new_qty, total_price, item_id),
            )
        else:
            total_price = quantity * price_per_unit
            cursor.execute(
                """
                INSERT INTO inventory (name, quantity, price_per_kg, total_price, category)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name_normalized, quantity, price_per_unit, total_price, category_normalized),
            )

        conn.commit()
        conn.close()

    def list_all(self) -> list:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_item(self, item_id: int, quantity: int, price_per_unit: float) -> None:
        total_price = quantity * price_per_unit
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE inventory
            SET quantity = ?, price_per_kg = ?, total_price = ?
            WHERE id = ?
            """,
            (quantity, price_per_unit, total_price, item_id),
        )
        conn.commit()
        conn.close()

    def delete_item(self, item_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    def update_name(self, item_id: int, name: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE inventory SET name = ? WHERE id = ?",
            (name.strip().lower(), item_id),
        )
        conn.commit()
        conn.close()

    def update_category(self, item_id: int, category: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE inventory SET category = ? WHERE id = ?",
            (category.strip().lower(), item_id),
        )
        conn.commit()
        conn.close()


