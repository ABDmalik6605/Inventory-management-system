import tkinter as tk
from tkinter import messagebox
import sqlite3

class InventoryDataOperations:
    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager
        
    def add_item(self):
        """Add or update an item in the inventory"""
        name = self.inventory_manager.ui_components.product_name_var.get().strip().lower()
        qty = self.inventory_manager.ui_components.product_quantity_var.get()
        price_per_kg = self.inventory_manager.ui_components.product_price_var.get()
        category = self.inventory_manager.ui_components.product_category_var.get().strip().lower()

        if not name or qty is None or price_per_kg is None or name == "":
            self._show_input_error_dialog()
            return

        if qty < 0 or price_per_kg < 0:
            messagebox.showwarning("Invalid Input", "Stock and Unit Price cannot be negative.")
            return

        try:
            self.inventory_manager.repo.add_or_update(name, qty, price_per_kg, category)
        except ValueError as e:
            if str(e) == "PRICE_CONFLICT":
                messagebox.showwarning("Price Error", "An item with the same name but a different price already exists!")
                return
            raise
        self.inventory_manager.ui_components.clear_inputs()
        self.inventory_manager.view_inventory()
        
    def _show_input_error_dialog(self):
        """Show a custom input error dialog"""
        dialog = tk.Toplevel(self.inventory_manager.root)
        dialog.title("Input Error")
        dialog.transient(self.inventory_manager.root)
        dialog.grab_set()

        # Target size and center positioning relative to parent
        width, height = 420, 180
        try:
            self.inventory_manager.root.update_idletasks()
            x = self.inventory_manager.root.winfo_x() + (self.inventory_manager.root.winfo_width() - width) // 2
            y = self.inventory_manager.root.winfo_y() + (self.inventory_manager.root.winfo_height() - height) // 2
            dialog.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            dialog.geometry(f"{width}x{height}")

        # Centered content with similar look
        content = ttk.Frame(dialog, padding=20)
        content.pack(expand=True, fill='both')
        message_label = ttk.Label(
            content,
            text="All fields except category are required!",
            font=('Segoe UI', 13),
            anchor='center',
            justify='center'
        )
        message_label.pack(expand=True)
        # Blue primary OK button
        btn_style = ttk.Style(dialog)
        btn_style.configure('WarnPrimary.TButton', background='#2563eb', foreground='white', padding=(10, 6))
        btn_style.map('WarnPrimary.TButton', background=[('active', '#1d4ed8'), ('pressed', '#1d4ed8')])
        ttk.Button(content, text="OK", command=dialog.destroy, style='WarnPrimary.TButton').pack(pady=(0, 10))
        
    def view_inventory(self, search_query: str = ""):
        """Display inventory data in the table"""
        if search_query:
            # Fallback to raw query for filtered view to avoid over-abstracting
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            like = f"%{search_query.strip().lower()}%"
            cursor.execute(
                "SELECT * FROM inventory WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?",
                (like, like),
            )
            rows = cursor.fetchall()
            conn.close()
        else:
            rows = self.inventory_manager.repo.list_all()

        # Clear the tree before inserting
        for row in self.inventory_manager.table_manager.inventory_tree.get_children():
            self.inventory_manager.table_manager.inventory_tree.delete(row)

        total_stock_value = 0.0
        total_sales_value = 0.0
        for index, row in enumerate(rows):
            # DB row order: (id, name, quantity, price_per_kg, total_price, category, sold_quantity, sold_total_cost)
            # UI order: (ID, Item, Stock, Unit Price, Stock Value, Category, Sales, Sales Value)
            id_val = row[0]
            name_val = row[1]
            qty_val = row[2]
            price_val = row[3]
            total_price_val = row[4]
            category_val = row[5] if len(row) > 5 else ""
            sold_qty_val = row[6] if len(row) > 6 else 0
            sold_total_cost_val = row[7] if len(row) > 7 else (sold_qty_val * price_val)
            # accumulate totals
            try:
                total_stock_value += float(total_price_val or 0)
            except Exception:
                pass
            try:
                total_sales_value += float(sold_total_cost_val or 0)
            except Exception:
                pass
            ui_row = (
                id_val,
                name_val,
                qty_val,
                price_val,
                total_price_val,
                category_val,
                sold_qty_val,
                sold_total_cost_val,
            )
            tag = 'oddrow' if index % 2 else 'evenrow'
            tree_row = self.inventory_manager.table_manager.inventory_tree.insert("", tk.END, values=ui_row, tags=(tag,))
            # Create persistent +/- controls for this row immediately after insert
            self.inventory_manager.root.after(0, lambda: self.inventory_manager.navigation_manager.position_divider_and_controls(self.inventory_manager.table_manager))

        # Also refocus search on refresh for quick filtering
        if hasattr(self.inventory_manager.ui_components, 'search_entry'):
            self.inventory_manager.ui_components.search_entry.focus_set()
        # Update total labels
        if hasattr(self.inventory_manager.ui_components, 'total_stock_var'):
            self.inventory_manager.ui_components.total_stock_var.set(f"{total_stock_value:.2f}")
        if hasattr(self.inventory_manager.ui_components, 'total_sales_var'):
            self.inventory_manager.ui_components.total_sales_var.set(f"{total_sales_value:.2f}")
            
    def delete_item_by_tree(self, item):
        """Delete an item from the tree view"""
        values = self.inventory_manager.table_manager.inventory_tree.item(item, "values")
        if not values:
            return
        item_id = values[0]
        item_name = values[1] if len(values) > 1 else "this item"
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{item_name}' (ID: {item_id})?",
        )
        if confirm:
            self.delete_item(item_id)
            
    def delete_item(self, item_id):
        """Delete an item by ID"""
        self.inventory_manager.repo.delete_item(item_id)
        self.view_inventory()
        messagebox.showinfo("Deleted", "Item deleted successfully!")
        
    def update_quantity_and_price(self, item_id, new_qty, new_price_per_kg):
        """Update item quantity and price"""
        # Recalculate the total price based on the new values
        total_price = new_qty * new_price_per_kg
        
        # Update the database with the new quantity, price per kg, and total price
        self.inventory_manager.repo.update_item(item_id, new_qty, new_price_per_kg)

        self.view_inventory()
        messagebox.showinfo("Updated", "Item updated successfully!")
        
    def adjust_sold(self, row_id, delta):
        """Adjust sold quantity for a specific row"""
        # delta is absolute; positive means increase sold by delta, negative decrease
        values = list(self.inventory_manager.table_manager.inventory_tree.item(row_id, 'values'))
        if not values:
            return
        try:
            item_id = int(values[0])
            remaining_qty = int(values[2])
            price = float(values[3])
            existing_sold = int(values[6]) if values[6] not in (None, '') else 0
        except Exception:
            return

        total_original = remaining_qty + existing_sold
        new_sold = max(0, min(total_original, existing_sold + delta))
        if new_sold == existing_sold:
            return
        # Persist and update UI
        try:
            self.inventory_manager.repo.update_sold(item_id, new_sold)
        except Exception:
            return

        new_remaining = total_original - new_sold
        values[2] = new_remaining
        values[6] = new_sold
        values[4] = new_remaining * price
        values[7] = new_sold * price
        self.inventory_manager.table_manager.inventory_tree.item(row_id, values=values)
        # Update footer totals
        try:
            self._refresh_totals_labels()
        except Exception:
            pass

    def adjust_stock(self, row_id, delta):
        """Adjust stock quantity for a specific row"""
        # delta is absolute; positive means increase remaining stock by delta, negative decrease
        values = list(self.inventory_manager.table_manager.inventory_tree.item(row_id, 'values'))
        if not values:
            return
        try:
            item_id = int(values[0])
            remaining_qty = int(values[2])
            price = float(values[3])
            existing_sold = int(values[6]) if values[6] not in (None, '') else 0
        except Exception:
            return

        new_remaining = max(0, remaining_qty + delta)
        # Persist remaining stock via update_item (keeps sold as-is)
        try:
            self.inventory_manager.repo.update_item(item_id, new_remaining, price)
        except Exception:
            return

        values[2] = new_remaining
        values[4] = new_remaining * price
        # Sales value remains consistent with same price
        values[7] = (int(values[6]) if values[6] not in (None, '') else 0) * price
        self.inventory_manager.table_manager.inventory_tree.item(row_id, values=values)
        try:
            self._refresh_totals_labels()
        except Exception:
            pass

    def _refresh_totals_labels(self):
        """Refresh the totals labels in the footer"""
        # Recompute totals from current tree (fast enough for moderate row counts)
        total_stock_value = 0.0
        total_sales_value = 0.0
        for iid in self.inventory_manager.table_manager.inventory_tree.get_children(''):
            vals = self.inventory_manager.table_manager.inventory_tree.item(iid, 'values')
            if not vals:
                continue
            try:
                total_stock_value += float(vals[4] or 0)
            except Exception:
                pass
            try:
                total_sales_value += float(vals[7] or 0)
            except Exception:
                pass
        if hasattr(self.inventory_manager.ui_components, 'total_stock_var'):
            self.inventory_manager.ui_components.total_stock_var.set(f"{total_stock_value:.2f}")
        if hasattr(self.inventory_manager.ui_components, 'total_sales_var'):
            self.inventory_manager.ui_components.total_sales_var.set(f"{total_sales_value:.2f}")
            
    def show_context_menu(self, event):
        """Show context menu for right-click on table"""
        item = self.inventory_manager.table_manager.inventory_tree.identify_row(event.y)
        if item:
            self.inventory_manager.table_manager.inventory_tree.selection_set(item)

            context_menu = tk.Menu(self.inventory_manager.root, tearoff=0)
            context_menu.add_command(label="Delete", command=lambda: self.delete_item_by_tree(item))
            context_menu.post(event.x_root, event.y_root)
