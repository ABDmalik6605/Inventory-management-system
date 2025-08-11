import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from app.inventory_repository import InventoryRepository

class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.repo = InventoryRepository()

    def create_inventory_tab(self, container):
        # Create content area inside the provided container (no tabs)
        inventory_view = ttk.Frame(container)
        inventory_view.pack(fill=tk.BOTH, expand=True)
        self.setup_inventory_tab(inventory_view)
        return inventory_view

    def setup_inventory_tab(self, tab):
        # Top container with subtle card style and divider
        header_container = ttk.Frame(tab, padding=(12, 8))
        header_container.pack(padx=12, pady=(10, 6), fill=tk.X)
        header_line = ttk.Separator(tab, orient='horizontal')
        header_line.pack(fill=tk.X, padx=12, pady=(0, 8))

        # Compact toolbar-style input area in a grid with consistent spacing
        input_frame = ttk.Frame(header_container)
        input_frame.pack(fill=tk.X)
        toolbar_font = ('Segoe UI', 12)

        # Input fields laid out in a single compact row
        ttk.Label(input_frame, text="Product Name", font=toolbar_font).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="w")
        self.product_name_var = tk.StringVar()
        self.product_name_entry = ttk.Entry(input_frame, textvariable=self.product_name_var, width=24, font=toolbar_font)
        self.product_name_entry.grid(row=0, column=1, padx=(0, 16), pady=4, sticky="ew")

        ttk.Label(input_frame, text="Quantity", font=toolbar_font).grid(row=0, column=2, padx=(0, 6), pady=4, sticky="w")
        self.product_quantity_var = tk.IntVar()
        self.product_quantity_entry = ttk.Entry(input_frame, textvariable=self.product_quantity_var, width=8, font=toolbar_font)
        self.product_quantity_entry.grid(row=0, column=3, padx=(0, 16), pady=4, sticky="w")

        ttk.Label(input_frame, text="Price per Unit", font=toolbar_font).grid(row=0, column=4, padx=(0, 6), pady=4, sticky="w")
        self.product_price_var = tk.DoubleVar()
        self.product_price_entry = ttk.Entry(input_frame, textvariable=self.product_price_var, width=10, font=toolbar_font)
        self.product_price_entry.grid(row=0, column=5, padx=(0, 16), pady=4, sticky="w")

        ttk.Label(input_frame, text="Category", font=toolbar_font).grid(row=0, column=6, padx=(0, 6), pady=4, sticky="w")
        self.product_category_var = tk.StringVar()
        self.product_category_entry = ttk.Entry(input_frame, textvariable=self.product_category_var, width=14, font=toolbar_font)
        self.product_category_entry.grid(row=0, column=7, padx=(0, 16), pady=4, sticky="ew")

        add_button = ttk.Button(input_frame, text="➕ Add", command=self.add_item, style='Add.TButton')
        add_button.grid(row=0, column=8, padx=(0, 16), pady=2, sticky="w")

        # Search/filter on the far right
        # Search group aligned to the right, label and field connected, icon inside button
        search_group = ttk.Frame(input_frame)
        search_group.grid(row=0, column=9, columnspan=3, sticky='e', padx=(0, 0))
        ttk.Label(search_group, text="Search", font=toolbar_font).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="e")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_group, textvariable=self.search_var, width=26, font=toolbar_font)
        self.search_entry.grid(row=0, column=1, padx=(0, 6), pady=4)
        self.search_entry.bind("<KeyRelease>", lambda e: self.view_inventory(self.search_var.get()))
        search_group.columnconfigure(1, weight=1)

        # Make toolbar responsive: expand Product Name and Category; push Search to the right
        input_frame.columnconfigure(1, weight=2)
        input_frame.columnconfigure(7, weight=1)
        input_frame.columnconfigure(8, weight=0)  # add button
        input_frame.columnconfigure(9, weight=1)  # spacer before search group

        # Table container
        table_shell = ttk.Frame(tab, padding=(12, 8))
        table_shell.pack(pady=(0, 12), padx=12, fill=tk.BOTH, expand=True)
        # Subtle table border effect using an inner frame
        table_frame = ttk.Frame(table_shell)
        table_frame.pack(pady=0, padx=8, fill=tk.BOTH, expand=True)

        # Bind arrow keys for navigation
        self.product_name_entry.bind("<Down>", self.move_to_quantity)
        self.product_quantity_entry.bind("<Up>", self.move_to_product_name)
        self.product_quantity_entry.bind("<Down>", self.move_to_price)
        self.product_price_entry.bind("<Up>", self.move_to_quantity)
        self.product_price_entry.bind("<Down>", self.move_to_category)
        self.product_category_entry.bind("<Up>", self.move_to_price)

        # Buttons moved to toolbar row (see above)

        # Inventory Table
        self.inventory_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Quantity", "Price per Unit", "Total Price", "Category"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.heading("Price per Unit", text="Price per Unit")
        self.inventory_tree.heading("Total Price", text="Total Price")
        self.inventory_tree.heading("Category", text="Category")
        
        for col in ["ID", "Name", "Quantity", "Price per Unit", "Total Price", "Category"]:
            self.inventory_tree.column(col, anchor="center")
        # Adjust column widths and alignment for readability
        self.inventory_tree.column("ID", width=60, anchor="center")
        self.inventory_tree.column("Name", width=260, anchor="w")
        self.inventory_tree.column("Quantity", width=120, anchor="center")
        self.inventory_tree.column("Price per Unit", width=140, anchor="center")
        self.inventory_tree.column("Total Price", width=140, anchor="center")
        self.inventory_tree.column("Category", width=220, anchor="w")

        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.inventory_tree.xview)
        self.inventory_tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Light border around table container using separators
        border_top = ttk.Separator(table_shell, orient='horizontal')
        border_top.pack(fill=tk.X, pady=(0, 8))

        # Zebra striping for a cleaner look
        self.inventory_tree.tag_configure('oddrow', background='#f9f9f9')
        self.inventory_tree.tag_configure('evenrow', background='#ffffff')
        # Enable sorting by clicking column headers
        self._setup_sortable_columns()
        # Enable inline editing on double-click
        self.inventory_tree.bind('<Double-1>', self._on_tree_double_click)
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
            # Custom larger warning dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Input Error")
            dialog.transient(self.root)
            dialog.grab_set()

            # Target size and center positioning relative to parent
            width, height = 420, 180
            try:
                self.root.update_idletasks()
                x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
                y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
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
            return

        try:
            self.repo.add_or_update(name, qty, price_per_kg, category)
        except ValueError as e:
            if str(e) == "PRICE_CONFLICT":
                messagebox.showwarning("Price Error", "An item with the same name but a different price already exists!")
                return
            raise
        self.clear_inputs()
        self.view_inventory()

    def view_inventory(self, search_query: str = ""):
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
            rows = self.repo.list_all()

        # Clear the tree before inserting
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        for index, row in enumerate(rows):
            tag = 'oddrow' if index % 2 else 'evenrow'
            self.inventory_tree.insert("", tk.END, values=row, tags=(tag,))

        # Bind right-click menu
        self.inventory_tree.bind("<Button-3>", self.show_context_menu)
        # Also refocus search on refresh for quick filtering
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()
        
    def show_context_menu(self, event):
        item = self.inventory_tree.identify_row(event.y)
        if item:
            self.inventory_tree.selection_set(item)

            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Delete", command=lambda: self.delete_item_by_tree(item))
            context_menu.post(event.x_root, event.y_root)

    # Legacy edit dialog removed in favor of inline editing

    def _on_tree_double_click(self, event):
        region = self.inventory_tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        row_id = self.inventory_tree.identify_row(event.y)
        col_id = self.inventory_tree.identify_column(event.x)
        if not row_id or not col_id:
            return

        # Map columns to editable fields (skip ID '#1' and Total Price '#5')
        editable_map = {
            '#2': ('name', 1),
            '#3': ('quantity', 2),
            '#4': ('price', 3),
            '#6': ('category', 5),
        }
        if col_id not in editable_map:
            return

        field, value_index = editable_map[col_id]
        bbox = self.inventory_tree.bbox(row_id, col_id)
        if not bbox:
            return
        x, y, width, height = bbox
        current_values = list(self.inventory_tree.item(row_id, 'values'))
        current_value = current_values[value_index]

        editor = ttk.Entry(self.inventory_tree)
        editor.place(x=x, y=y, width=width, height=height)
        editor.insert(0, str(current_value))
        editor.focus()

        def commit():
            new_text = editor.get().strip()
            item_id = int(current_values[0])
            try:
                if field == 'name':
                    if not new_text:
                        raise ValueError('Name cannot be empty')
                    from app.inventory_repository import InventoryRepository
                    self.repo.update_name(item_id, new_text)
                    current_values[1] = new_text
                elif field == 'category':
                    from app.inventory_repository import InventoryRepository
                    self.repo.update_category(item_id, new_text)
                    current_values[5] = new_text
                elif field == 'quantity':
                    quantity = int(new_text)
                    price = float(current_values[3])
                    self.repo.update_item(item_id, quantity, price)
                    current_values[2] = quantity
                    current_values[4] = quantity * price
                elif field == 'price':
                    price = float(new_text)
                    quantity = int(current_values[2])
                    self.repo.update_item(item_id, quantity, price)
                    current_values[3] = price
                    current_values[4] = quantity * price
                self.inventory_tree.item(row_id, values=current_values)
                editor.destroy()
            except Exception:
                editor.destroy()

        editor.bind('<Return>', lambda e: commit())
        editor.bind('<FocusOut>', lambda e: editor.destroy())

    def update_quantity_and_price(self, item_id, new_qty, new_price_per_kg):
        # Recalculate the total price based on the new values
        total_price = new_qty * new_price_per_kg
        
        # Update the database with the new quantity, price per kg, and total price
        self.repo.update_item(item_id, new_qty, new_price_per_kg)

        self.view_inventory()
        messagebox.showinfo("Updated", "Item updated successfully!")

    def _setup_sortable_columns(self):
        def sort_by(col, reverse=False):
            # Fetch all items
            items = [(self.inventory_tree.set(k, col), k) for k in self.inventory_tree.get_children("")]
            # Convert numerics where applicable
            def try_float(v):
                try:
                    return float(v)
                except ValueError:
                    return v
            items.sort(key=lambda t: try_float(t[0]), reverse=reverse)
            # Reorder items
            for index, (_, k) in enumerate(items):
                self.inventory_tree.move(k, "", index)
            # Toggle next sort order
            self.inventory_tree.heading(col, command=lambda: sort_by(col, not reverse))

        for col in ("ID", "Name", "Quantity", "Price per Unit", "Total Price", "Category"):
            self.inventory_tree.heading(col, text=col, command=lambda c=col: sort_by(c, False))

    def delete_item_by_tree(self, item):
        values = self.inventory_tree.item(item, "values")
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

    def clear_inputs(self):
        self.product_name_var.set("")
        self.product_quantity_var.set(0)
        self.product_price_var.set(0.0)
        self.product_category_var.set("")

    def delete_item(self, item_id):
        self.repo.delete_item(item_id)
        self.view_inventory()
        messagebox.showinfo("Deleted", "Item deleted successfully!")