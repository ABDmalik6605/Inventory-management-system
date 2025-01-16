import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class InventoryManager:
    def __init__(self, root):
        self.root = root

    def create_inventory_tab(self, notebook):
        # Inventory Tab UI setup (similar to original setup_inventory_tab)
        inventory_tab = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(inventory_tab, text="Inventory")
        self.setup_inventory_tab(inventory_tab)
        return inventory_tab

    def setup_inventory_tab(self, tab):
        # input_frame = tk.Frame(tab, padx=10, pady=10, bg="#ffffff", relief="groove")
        # input_frame.pack(pady=10, fill=tk.X)

        # Define input fields, buttons, and table (similar to original setup_inventory_tab)
        # Use self.add_item() and self.view_inventory() for functionality
        # Frames for layout
        input_frame = tk.Frame(tab,padx=10, pady=10, bg="#ffffff", relief="groove")
        input_frame.pack(pady=10, fill=tk.X)

        table_frame = tk.Frame(tab,padx=10, pady=10, bg="#ffffff", relief="groove")
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Input fields
        tk.Label(input_frame, text="Product Name", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.product_name_var = tk.StringVar()
        self.product_name_entry = tk.Entry(input_frame, textvariable=self.product_name_var)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Quantity", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5)
        self.product_quantity_var = tk.IntVar()
        self.product_quantity_entry = tk.Entry(input_frame, textvariable=self.product_quantity_var)
        self.product_quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Price per KG", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5)
        self.product_price_var = tk.DoubleVar()
        self.product_price_entry = tk.Entry(input_frame, textvariable=self.product_price_var)
        self.product_price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Category", bg="#ffffff").grid(row=3, column=0, padx=5, pady=5)
        self.product_category_var = tk.StringVar()
        self.product_category_entry = tk.Entry(input_frame, textvariable=self.product_category_var)
        self.product_category_entry.grid(row=3, column=1, padx=5, pady=5)

        # Bind arrow keys for navigation
        self.product_name_entry.bind("<Down>", self.move_to_quantity)
        self.product_quantity_entry.bind("<Up>", self.move_to_product_name)
        self.product_quantity_entry.bind("<Down>", self.move_to_price)
        self.product_price_entry.bind("<Up>", self.move_to_quantity)
        self.product_price_entry.bind("<Down>", self.move_to_category)
        self.product_category_entry.bind("<Up>", self.move_to_price)

        # Buttons
        tk.Button(input_frame, text="Add Product", command=self.add_item, bg="#4caf50", fg="white").grid(row=4, column=0, padx=5, pady=10)
        tk.Button(input_frame, text="View Inventory", command=self.view_inventory, bg="#2196f3", fg="white").grid(row=4, column=1, padx=5, pady=10)

        # Inventory Table
        self.inventory_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Quantity", "Price per KG", "Total Price", "Category"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.heading("Price per KG", text="Price per KG")
        self.inventory_tree.heading("Total Price", text="Total Price")
        self.inventory_tree.heading("Category", text="Category")
        
        for col in ["ID", "Name", "Quantity", "Price per KG", "Total Price", "Category"]:
            self.inventory_tree.column(col, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        self.view_inventory()
        
    #Cursor movements
    def move_to_product_name(self, event=None):
        self.product_name_entry.focus_set()

    def move_to_quantity(self, event=None):
        self.product_quantity_entry.focus_set()

    def move_to_price(self, event=None):
        self.product_price_entry.focus_set()

    def move_to_category(self, event=None):
        self.product_category_entry.focus_set()

    def add_item(self):
        name = self.product_name_var.get().strip().lower()
        qty = self.product_quantity_var.get()
        price_per_kg = self.product_price_var.get()
        category = self.product_category_var.get().strip().lower()

        if not name or not qty or not price_per_kg:
            messagebox.showwarning("Input Error", "All fields except category are required!")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        # Check if an item with the same name (case-insensitive) exists and has a different price_per_kg
        cursor.execute("""
            SELECT id, quantity, price_per_kg FROM inventory 
            WHERE LOWER(name) = ? AND price_per_kg != ? 
        """, (name, price_per_kg))
        
        existing_item = cursor.fetchone()

        if existing_item:
            # If item with the same name exists but different price per kg, show error
            messagebox.showwarning("Price Error", "An item with the same name but a different price already exists!")
            conn.close()
            return

        # Check if an item with the same name and price per kg (case-insensitive) exists
        cursor.execute("""
            SELECT id, quantity, price_per_kg FROM inventory 
            WHERE LOWER(name) = ? AND price_per_kg = ?
        """, (name, price_per_kg))
        existing_item = cursor.fetchone()

        if existing_item:
            # Update quantity and total price of the existing item
            item_id, existing_qty, _ = existing_item
            new_qty = existing_qty + qty
            total_price = new_qty * price_per_kg
            cursor.execute("""
                UPDATE inventory
                SET quantity = ?, total_price = ?
                WHERE id = ?
            """, (new_qty, total_price, item_id))
        else:
            # Add new item
            total_price = qty * price_per_kg
            cursor.execute("""
                INSERT INTO inventory (name, quantity, price_per_kg, total_price, category)
                VALUES (?, ?, ?, ?, ?)
            """, (name, qty, price_per_kg, total_price, category))

        conn.commit()
        conn.close()

        self.clear_inputs()
        self.view_inventory()

    def view_inventory(self):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        conn.close()

        # Clear the tree before inserting
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        for row in rows:
            self.inventory_tree.insert("", tk.END, values=row)

        # Bind right-click menu
        self.inventory_tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        item = self.inventory_tree.identify_row(event.y)
        if item:
            self.inventory_tree.selection_set(item)

            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Edit", command=lambda: self.edit_item(item))
            context_menu.add_command(label="Delete", command=lambda: self.delete_item_by_tree(item))
            context_menu.post(event.x_root, event.y_root)

    def edit_item(self, item):
        item_id = self.inventory_tree.item(item, "values")[0]
        current_qty = self.inventory_tree.item(item, "values")[2]
        current_price = self.inventory_tree.item(item, "values")[3]

        # Create a custom dialog for editing
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Item")
        dialog.geometry("300x200")
        dialog.transient(self.root)  # Make it a child of the main window
        dialog.grab_set()  # Make it modal

        # Quantity input
        tk.Label(dialog, text="New Quantity:").pack(pady=5)
        qty_var = tk.IntVar(value=current_qty)
        tk.Entry(dialog, textvariable=qty_var).pack(pady=5)

        # Price per kg input
        tk.Label(dialog, text="New Price per kg:").pack(pady=5)
        price_var = tk.DoubleVar(value=current_price)
        tk.Entry(dialog, textvariable=price_var).pack(pady=5)

        # Buttons
        def save_changes():
            new_qty = qty_var.get()
            new_price_per_kg = price_var.get()
            if new_qty is not None and new_price_per_kg is not None:
                self.update_quantity_and_price(item_id, new_qty, new_price_per_kg)
            dialog.destroy()

        tk.Button(dialog, text="Save", command=save_changes).pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

        dialog.mainloop()

    def update_quantity_and_price(self, item_id, new_qty, new_price_per_kg):
        # Recalculate the total price based on the new values
        total_price = new_qty * new_price_per_kg
        
        # Update the database with the new quantity, price per kg, and total price
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inventory 
            SET quantity = ?, price_per_kg = ?, total_price = ? 
            WHERE id = ?
        """, (new_qty, new_price_per_kg, total_price, item_id))
        conn.commit()
        conn.close()

        self.view_inventory()
        messagebox.showinfo("Updated", "Item updated successfully!")

    def delete_item_by_tree(self, item):
        item_id = self.inventory_tree.item(item, "values")[0]
        self.delete_item(item_id)

    def clear_inputs(self):
        self.product_name_var.set("")
        self.product_quantity_var.set(0)
        self.product_price_var.set(0.0)
        self.product_category_var.set("")

    def delete_item(self, item_id):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        self.view_inventory()
        messagebox.showinfo("Deleted", "Item deleted successfully!")