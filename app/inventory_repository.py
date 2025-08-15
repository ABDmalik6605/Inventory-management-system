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
                INSERT INTO inventory (name, quantity, price_per_kg, total_price, category, sold_quantity, sold_total_cost)
                VALUES (?, ?, ?, ?, ?, 0, 0.0)
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
        # Get current sold_quantity to recompute sold_total_cost with the new price
        cursor.execute("SELECT COALESCE(sold_quantity, 0) FROM inventory WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        current_sold = row[0] if row else 0
        sold_total_cost = current_sold * price_per_unit
        cursor.execute(
            """
            UPDATE inventory
            SET quantity = ?, price_per_kg = ?, total_price = ?, sold_total_cost = ?
            WHERE id = ?
            """,
            (quantity, price_per_unit, total_price, sold_total_cost, item_id),
        )
        conn.commit()
        conn.close()

    def update_sold(self, item_id: int, sold_quantity: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        # Fetch current quantity, current sold and price
        cursor.execute("SELECT quantity, COALESCE(sold_quantity, 0), price_per_kg FROM inventory WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError("ITEM_NOT_FOUND")
        current_qty, existing_sold, price_per_unit = row
        if sold_quantity < 0:
            conn.close()
            raise ValueError("INVALID_SOLD_QTY")
        total_original = current_qty + existing_sold
        if sold_quantity > total_original:
            conn.close()
            raise ValueError("INVALID_SOLD_QTY")

        remaining_qty = total_original - sold_quantity
        new_total_price = remaining_qty * price_per_unit
        sold_total_cost = sold_quantity * price_per_unit

        cursor.execute(
            """
            UPDATE inventory
            SET quantity = ?, total_price = ?, sold_quantity = ?, sold_total_cost = ?
            WHERE id = ?
            """,
            (remaining_qty, new_total_price, sold_quantity, sold_total_cost, item_id),
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


