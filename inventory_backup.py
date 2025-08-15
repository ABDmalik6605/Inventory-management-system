import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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
        ttk.Label(input_frame, text="Item", font=toolbar_font).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="w")
        self.product_name_var = tk.StringVar()
        self.product_name_entry = ttk.Entry(input_frame, textvariable=self.product_name_var, width=24, font=toolbar_font)
        self.product_name_entry.grid(row=0, column=1, padx=(0, 16), pady=4, sticky="ew")

        ttk.Label(input_frame, text="Stock", font=toolbar_font).grid(row=0, column=2, padx=(0, 6), pady=4, sticky="w")
        self.product_quantity_var = tk.IntVar()
        self.product_quantity_entry = ttk.Entry(input_frame, textvariable=self.product_quantity_var, width=8, font=toolbar_font)
        self.product_quantity_entry.grid(row=0, column=3, padx=(0, 16), pady=4, sticky="w")

        ttk.Label(input_frame, text="Unit Price", font=toolbar_font).grid(row=0, column=4, padx=(0, 6), pady=4, sticky="w")
        self.product_price_var = tk.DoubleVar()
        self.product_price_entry = ttk.Entry(input_frame, textvariable=self.product_price_var, width=10, font=toolbar_font)
        self.product_price_entry.grid(row=0, column=5, padx=(0, 16), pady=4, sticky="w")

        ttk.Label(input_frame, text="Category", font=toolbar_font).grid(row=0, column=6, padx=(0, 6), pady=4, sticky="w")
        self.product_category_var = tk.StringVar()
        self.product_category_entry = ttk.Entry(input_frame, textvariable=self.product_category_var, width=14, font=toolbar_font)
        self.product_category_entry.grid(row=0, column=7, padx=(0, 16), pady=4, sticky="ew")

        add_button = ttk.Button(input_frame, text="➕ Add", command=self.add_item, style='Add.TButton')
        add_button.grid(row=0, column=8, padx=(0, 16), pady=2, sticky="w")

        # Left/Right navigation between fields (only when caret at ends) and Enter to Add
        self.product_name_entry.bind("<Right>", lambda e: self._move_if_at_end(self.product_name_entry, self.product_quantity_entry))
        self.product_name_entry.bind("<Left>", lambda e: self._move_if_at_start(self.product_name_entry, self.product_category_entry))
        self.product_name_entry.bind("<Return>", lambda e: (self.add_item(), "break"))

        self.product_quantity_entry.bind("<Right>", lambda e: self._move_if_at_end(self.product_quantity_entry, self.product_price_entry))
        self.product_quantity_entry.bind("<Left>", lambda e: self._move_if_at_start(self.product_quantity_entry, self.product_name_entry))
        self.product_quantity_entry.bind("<Return>", lambda e: (self.add_item(), "break"))

        self.product_price_entry.bind("<Right>", lambda e: self._move_if_at_end(self.product_price_entry, self.product_category_entry))
        self.product_price_entry.bind("<Left>", lambda e: self._move_if_at_start(self.product_price_entry, self.product_quantity_entry))
        self.product_price_entry.bind("<Return>", lambda e: (self.add_item(), "break"))

        self.product_category_entry.bind("<Right>", lambda e: self._move_if_at_end(self.product_category_entry, self.product_name_entry))
        self.product_category_entry.bind("<Left>", lambda e: self._move_if_at_start(self.product_category_entry, self.product_price_entry))
        self.product_category_entry.bind("<Return>", lambda e: (self.add_item(), "break"))

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
        self.inventory_tree = ttk.Treeview(
            table_frame,
            columns=(
                "ID",
                "Item",
                "Stock",
                "Unit Price",
                "Stock Value",
                "Category",
                "Sales",
                "Sales Value",
            ),
            show="headings",
        )
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Item", text="Item")
        self.inventory_tree.heading("Stock", text="Stock")
        self.inventory_tree.heading("Unit Price", text="Unit Price")
        self.inventory_tree.heading("Stock Value", text="Stock Value")
        self.inventory_tree.heading("Category", text="Category")
        self.inventory_tree.heading("Sales", text="Sales")
        self.inventory_tree.heading("Sales Value", text="Sales Value")
        
        for col in [
            "ID",
            "Item",
            "Stock",
            "Unit Price",
            "Stock Value",
            "Category",
            "Sales",
            "Sales Value",
        ]:
            self.inventory_tree.column(col, anchor="center")
        # Adjust column widths and alignment for readability
        self.inventory_tree.column("ID", width=60, anchor="center")
        self.inventory_tree.column("Item", width=240, anchor="w")
        self.inventory_tree.column("Stock", width=110, anchor="center")
        self.inventory_tree.column("Unit Price", width=140, anchor="center")
        self.inventory_tree.column("Stock Value", width=140, anchor="center")
        self.inventory_tree.column("Category", width=180, anchor="w")
        self.inventory_tree.column("Sales", width=110, anchor="center")
        self.inventory_tree.column("Sales Value", width=150, anchor="center")

        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.inventory_tree.xview)
        self._scrollbar_y = scrollbar_y
        self._scrollbar_x = scrollbar_x
        # Wrap scroll commands so we can reposition divider and controls on scroll
        self.inventory_tree.configure(yscrollcommand=self._on_tree_yscroll, xscrollcommand=self._on_tree_xscroll)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Light border around table container using separators
        border_top = ttk.Separator(table_shell, orient='horizontal')
        border_top.pack(fill=tk.X, pady=(0, 8))

        # Footer totals bar at the bottom of the window
        footer_sep = ttk.Separator(tab, orient='horizontal')
        footer_sep.pack(fill=tk.X, padx=12, pady=(4, 0))
        footer = ttk.Frame(tab, padding=(12, 8))
        footer.pack(fill=tk.X, padx=0, pady=(4, 8))
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=0)
        footer.columnconfigure(2, weight=0)
        self.total_stock_var = tk.StringVar(value="0.00")
        self.total_sales_var = tk.StringVar(value="0.00")
        totals_container = ttk.Frame(footer)
        totals_container.grid(row=0, column=1, sticky='e')
        ttk.Label(totals_container, text="Total Stock Value:", font=('Segoe UI Semibold', 11)).grid(row=0, column=0, padx=(0,6))
        self.total_stock_label = ttk.Label(totals_container, textvariable=self.total_stock_var, font=('Segoe UI', 11))
        self.total_stock_label.grid(row=0, column=1, padx=(0,16))
        ttk.Label(totals_container, text="Total Sales Value:", font=('Segoe UI Semibold', 11)).grid(row=0, column=2, padx=(0,6))
        self.total_sales_label = ttk.Label(totals_container, textvariable=self.total_sales_var, font=('Segoe UI', 11))
        self.total_sales_label.grid(row=0, column=3)

        # Zebra striping for a cleaner look
        self.inventory_tree.tag_configure('oddrow', background='#f9f9f9')
        self.inventory_tree.tag_configure('evenrow', background='#ffffff')
        # Enable sorting by clicking column headers
        self._setup_sortable_columns()
        # Enable inline editing on double-click
        self.inventory_tree.bind('<Double-1>', self._on_tree_double_click)
        # Enable multi-select and bulk delete
        self.inventory_tree.configure(selectmode='extended')
        self.inventory_tree.bind('<Delete>', self._on_delete_selected)
        # Hover cursor hint for editable cells
        self.inventory_tree.bind('<Motion>', self._on_tree_motion_cursor)
        self.inventory_tree.bind('<Leave>', lambda e: self.inventory_tree.configure(cursor=''))
        # Persistent controls for Stock and Sales columns (+/- overlay labels for visible rows)
        self._sold_controls = {}  # row_id -> (minus_label, plus_label)
        self._stock_controls = {}  # row_id -> (minus_label, plus_label)
        self.inventory_tree.bind('<Configure>', lambda e: self._position_divider_and_controls())
        self.inventory_tree.bind('<<TreeviewSelect>>', lambda e: self._position_divider_and_controls())
        # Vertical divider between Category and Sold
        self._divider_line = tk.Frame(self.inventory_tree, bg='#111111', width=2)
        self._divider_line.place_forget()
        self._divider_glow = tk.Frame(self.inventory_tree, bg='#e5e7eb', width=1)
        self._divider_glow.place_forget()
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

    def _move_if_at_end(self, entry_widget, next_widget):
        try:
            if entry_widget.index(tk.INSERT) >= len(entry_widget.get()):
                next_widget.focus_set()
                return "break"
        except Exception:
            pass
        return None

    def _move_if_at_start(self, entry_widget, prev_widget):
        try:
            if entry_widget.index(tk.INSERT) <= 0:
                prev_widget.focus_set()
                return "break"
        except Exception:
            pass
        return None

    def add_item(self):
        name = self.product_name_var.get().strip().lower()
        qty = self.product_quantity_var.get()
        price_per_kg = self.product_price_var.get()
        category = self.product_category_var.get().strip().lower()

        if not name or qty is None or price_per_kg is None or name == "":
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

        if qty < 0 or price_per_kg < 0:
            messagebox.showwarning("Invalid Input", "Stock and Unit Price cannot be negative.")
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
            tree_row = self.inventory_tree.insert("", tk.END, values=ui_row, tags=(tag,))
            # Create persistent +/- controls for this row immediately after insert
            self.root.after(0, self._position_divider_and_controls)

        # Bind right-click menu
        self.inventory_tree.bind("<Button-3>", self.show_context_menu)
        # Also refocus search on refresh for quick filtering
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()
        # Update total labels
        if hasattr(self, 'total_stock_var'):
            self.total_stock_var.set(f"{total_stock_value:.2f}")
        if hasattr(self, 'total_sales_var'):
            self.total_sales_var.set(f"{total_sales_value:.2f}")
        
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
            '#2': ('name', 1),   # Item
            '#3': ('quantity', 2),  # Stock (remaining)
            '#4': ('price', 3),  # Unit Price
            '#6': ('category', 5),  # Category
            '#7': ('sold', 6),   # Sales (sold qty)
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
                    # Treat edited Quantity as remaining stock directly
                    remaining_qty = int(new_text)
                    if remaining_qty < 0:
                        raise ValueError('Quantity cannot be negative')
                    price = float(current_values[3])
                    self.repo.update_item(item_id, remaining_qty, price)
                    current_values[2] = remaining_qty
                    current_values[4] = remaining_qty * price
                    # Recompute sold total cost with unchanged sold
                    sold_qty = int(current_values[6]) if current_values[6] not in (None, '') else 0
                    current_values[7] = sold_qty * price
                elif field == 'sold':
                    sold_qty = int(new_text)
                    price = float(current_values[3])
                    available_qty = int(current_values[2])
                    existing_sold = int(current_values[6]) if current_values[6] not in (None, '') else 0
                    total_original = available_qty + existing_sold
                    if sold_qty < 0 or sold_qty > total_original:
                        raise ValueError('Invalid sold amount')
                    # Apply sold update to DB
                    self.repo.update_sold(item_id, sold_qty)
                    # Compute new remaining stock
                    new_remaining = total_original - sold_qty
                    current_values[2] = new_remaining
                    current_values[6] = sold_qty
                    current_values[4] = new_remaining * price
                    current_values[7] = sold_qty * price
                elif field == 'price':
                    price = float(new_text)
                    if price < 0:
                        raise ValueError('Price cannot be negative')
                    quantity = int(current_values[2])
                    self.repo.update_item(item_id, quantity, price)
                    current_values[3] = price
                    current_values[4] = quantity * price
                    # Recompute sold total cost
                    sold_qty = int(current_values[6]) if current_values[6] not in (None, '') else 0
                    current_values[7] = sold_qty * price
                self.inventory_tree.item(row_id, values=current_values)
                editor.destroy()
            except ValueError as ve:
                messagebox.showwarning("Invalid Input", str(ve))
                editor.destroy()
            except Exception:
                editor.destroy()

        editor.bind('<Return>', lambda e: commit())
        editor.bind('<FocusOut>', lambda e: editor.destroy())

    def _adjust_sold(self, row_id, delta):
        # delta is absolute; positive means increase sold by delta, negative decrease
        values = list(self.inventory_tree.item(row_id, 'values'))
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
            self.repo.update_sold(item_id, new_sold)
        except Exception:
            return

        new_remaining = total_original - new_sold
        values[2] = new_remaining
        values[6] = new_sold
        values[4] = new_remaining * price
        values[7] = new_sold * price
        self.inventory_tree.item(row_id, values=values)
        # Update footer totals
        try:
            self._refresh_totals_labels()
        except Exception:
            pass

    def _adjust_stock(self, row_id, delta):
        # delta is absolute; positive means increase remaining stock by delta, negative decrease
        values = list(self.inventory_tree.item(row_id, 'values'))
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
            self.repo.update_item(item_id, new_remaining, price)
        except Exception:
            return

        values[2] = new_remaining
        values[4] = new_remaining * price
        # Sales value remains consistent with same price
        values[7] = (int(values[6]) if values[6] not in (None, '') else 0) * price
        self.inventory_tree.item(row_id, values=values)
        try:
            self._refresh_totals_labels()
        except Exception:
            pass

    def _prompt_adjust_sold(self, row_id, sign):
        try:
            values = list(self.inventory_tree.item(row_id, 'values'))
        except Exception:
            return
        if not values:
            return
        prompt = "Increase Sales by" if sign > 0 else "Decrease Sales by"
        amount = simpledialog.askinteger("Adjust Sales", f"{prompt} (units):", parent=self.root, minvalue=0)
        if amount is None:
            return
        if amount < 0:
            messagebox.showwarning("Invalid Input", "Amount cannot be negative.")
            return
        # Validate bounds strictly: cannot sell more than remaining; cannot reduce sales below zero
        try:
            remaining_qty = int(values[2])
            existing_sold = int(values[6]) if values[6] not in (None, '') else 0
        except Exception:
            return
        if sign > 0 and amount > remaining_qty:
            messagebox.showwarning("Invalid Amount", "Cannot increase sales by more than current stock.")
            return
        if sign < 0 and amount > existing_sold:
            messagebox.showwarning("Invalid Amount", "Cannot decrease sales by more than current sales.")
            return
        delta = amount if sign > 0 else -amount
        self._adjust_sold(row_id, delta)

    def _prompt_adjust_stock(self, row_id, sign):
        try:
            values = list(self.inventory_tree.item(row_id, 'values'))
        except Exception:
            return
        if not values:
            return
        prompt = "Increase Stock by" if sign > 0 else "Decrease Stock by"
        amount = simpledialog.askinteger("Adjust Stock", f"{prompt} (units):", parent=self.root, minvalue=0)
        if amount is None:
            return
        if amount < 0:
            messagebox.showwarning("Invalid Input", "Amount cannot be negative.")
            return
        # Validate bounds strictly for stock decreases
        try:
            remaining_qty = int(values[2])
        except Exception:
            return
        if sign < 0 and amount > remaining_qty:
            messagebox.showwarning("Invalid Amount", "Cannot decrease stock by more than current stock.")
            return
        delta = amount if sign > 0 else -amount
        self._adjust_stock(row_id, delta)

    def _refresh_totals_labels(self):
        # Recompute totals from current tree (fast enough for moderate row counts)
        total_stock_value = 0.0
        total_sales_value = 0.0
        for iid in self.inventory_tree.get_children(''):
            vals = self.inventory_tree.item(iid, 'values')
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
        if hasattr(self, 'total_stock_var'):
            self.total_stock_var.set(f"{total_stock_value:.2f}")
        if hasattr(self, 'total_sales_var'):
            self.total_sales_var.set(f"{total_sales_value:.2f}")

    def _position_divider_and_controls(self):
        try:
            # Divider: compute x after Category column '#6' from header bbox
            # Use the first row bbox as fallback for x-position
            first_row = next(iter(self.inventory_tree.get_children('')), None)
            header_bbox = self.inventory_tree.bbox(first_row, '#6') if first_row else None
            if header_bbox:
                x, y, width, height = header_bbox
                x_pos = x + width - 1
                tree_height = self.inventory_tree.winfo_height()
                self._divider_line.place(x=x_pos, y=0, width=2, height=tree_height)
                self._divider_glow.place(x=x_pos+2, y=0, width=1, height=tree_height)
            else:
                self._divider_line.place_forget()
                self._divider_glow.place_forget()
        except Exception:
            pass

        # Controls: ensure +/- controls exist for each visible row in Stock column '#3'
        visible_rows = self.inventory_tree.get_children('')
        for row_id in visible_rows:
            bbox = self.inventory_tree.bbox(row_id, '#3')
            if not bbox:
                self._destroy_stock_controls(row_id)
                continue
            x, y, width, height = bbox
            minus_ctrl, plus_ctrl = self._stock_controls.get(row_id, (None, None))
            # Background based on selection/zebra
            bg = '#ffffff'
            try:
                if row_id in self.inventory_tree.selection():
                    bg = '#dbeafe'
                else:
                    tags = self.inventory_tree.item(row_id, 'tags')
                    bg = '#f9f9f9' if ('oddrow' in tags) else '#ffffff'
            except Exception:
                pass
            if minus_ctrl is None:
                minus_ctrl = tk.Label(self.inventory_tree, text='−', fg='#ef4444', bg=bg, cursor='hand2', font=('Segoe UI', 13, 'bold'))
                minus_ctrl.bind('<Button-1>', lambda e, r=row_id: self._prompt_adjust_stock(r, -1))
            if plus_ctrl is None:
                plus_ctrl = tk.Label(self.inventory_tree, text='+', fg='#2563eb', bg=bg, cursor='hand2', font=('Segoe UI', 13, 'bold'))
                plus_ctrl.bind('<Button-1>', lambda e, r=row_id: self._prompt_adjust_stock(r, +1))
            try:
                minus_ctrl.configure(bg=bg)
                plus_ctrl.configure(bg=bg)
            except Exception:
                pass
            btn_h = max(20, min(28, height-4))
            btn_w = 22
            minus_ctrl.place(x=x+3, y=y+2, width=btn_w, height=btn_h)
            plus_ctrl.place(x=x+width-btn_w-3, y=y+2, width=btn_w, height=btn_h)
            self._stock_controls[row_id] = (minus_ctrl, plus_ctrl)

        # Controls: ensure +/- controls exist for each visible row in Sales column '#7'
        visible_rows = self.inventory_tree.get_children('')
        for row_id in visible_rows:
            bbox = self.inventory_tree.bbox(row_id, '#7')
            if not bbox:
                # Row may be scrolled off; remove controls if any
                self._destroy_row_controls(row_id)
                continue
            x, y, width, height = bbox
            minus_ctrl, plus_ctrl = self._sold_controls.get(row_id, (None, None))
            # Determine background based on row state (selected/zebra)
            bg = '#ffffff'
            try:
                if row_id in self.inventory_tree.selection():
                    bg = '#dbeafe'
                else:
                    tags = self.inventory_tree.item(row_id, 'tags')
                    bg = '#f9f9f9' if ('oddrow' in tags) else '#ffffff'
            except Exception:
                pass
            if minus_ctrl is None:
                minus_ctrl = tk.Label(self.inventory_tree, text='−', fg='#ef4444', bg=bg, cursor='hand2', font=('Segoe UI', 13, 'bold'))
                minus_ctrl.bind('<Button-1>', lambda e, r=row_id: self._prompt_adjust_sold(r, -1))
            if plus_ctrl is None:
                plus_ctrl = tk.Label(self.inventory_tree, text='+', fg='#2563eb', bg=bg, cursor='hand2', font=('Segoe UI', 13, 'bold'))
                plus_ctrl.bind('<Button-1>', lambda e, r=row_id: self._prompt_adjust_sold(r, +1))
            # Update bg in case row selection/zebra changed
            try:
                minus_ctrl.configure(bg=bg)
                plus_ctrl.configure(bg=bg)
            except Exception:
                pass
            btn_h = max(20, min(28, height-4))
            btn_w = 22
            minus_ctrl.place(x=x+3, y=y+2, width=btn_w, height=btn_h)
            plus_ctrl.place(x=x+width-btn_w-3, y=y+2, width=btn_w, height=btn_h)
            self._sold_controls[row_id] = (minus_ctrl, plus_ctrl)

        # Remove controls for rows no longer visible
        for row_id in list(self._sold_controls.keys()):
            if row_id not in visible_rows:
                self._destroy_row_controls(row_id)
        for row_id in list(self._stock_controls.keys()):
            if row_id not in visible_rows:
                self._destroy_stock_controls(row_id)

    def _destroy_row_controls(self, row_id):
        minus_btn, plus_btn = self._sold_controls.pop(row_id, (None, None))
        try:
            if minus_btn is not None:
                minus_btn.place_forget()
                minus_btn.destroy()
        except Exception:
            pass
        try:
            if plus_btn is not None:
                plus_btn.place_forget()
                plus_btn.destroy()
        except Exception:
            pass

    def _destroy_stock_controls(self, row_id):
        minus_btn, plus_btn = self._stock_controls.pop(row_id, (None, None))
        try:
            if minus_btn is not None:
                minus_btn.place_forget()
                minus_btn.destroy()
        except Exception:
            pass
        try:
            if plus_btn is not None:
                plus_btn.place_forget()
                plus_btn.destroy()
        except Exception:
            pass

    def _on_tree_yscroll(self, *args):
        try:
            self._scrollbar_y.set(*args)
        except Exception:
            pass
        self._position_divider_and_controls()

    def _on_tree_xscroll(self, *args):
        try:
            self._scrollbar_x.set(*args)
        except Exception:
            pass
        self._position_divider_and_controls()

    def _on_tree_motion_cursor(self, event):
        try:
            region = self.inventory_tree.identify('region', event.x, event.y)
            if region != 'cell':
                self.inventory_tree.configure(cursor='')
                return
            col_id = self.inventory_tree.identify_column(event.x)
            # Editable columns: Item(#2), Stock(#3), Unit Price(#4), Category(#6), Sales(#7)
            if col_id in {'#2', '#3', '#4', '#6', '#7'}:
                self.inventory_tree.configure(cursor='xterm')  # I-beam text cursor
            else:
                self.inventory_tree.configure(cursor='')
        except Exception:
            self.inventory_tree.configure(cursor='')

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

        for col in ("ID", "Item", "Stock", "Unit Price", "Stock Value", "Category", "Sales", "Sales Value"):
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

    def _on_delete_selected(self, event=None):
        selected_items = self.inventory_tree.selection()
        if not selected_items:
            return
        # Gather IDs and names for message
        ids = []
        names = []
        for item in selected_items:
            vals = self.inventory_tree.item(item, 'values')
            if vals:
                ids.append(str(vals[0]))
                names.append(str(vals[1]))
        label_preview = ", ".join(names[:5]) + (" …" if len(names) > 5 else "")
        confirm = messagebox.askyesno(
            "Delete Selected",
            f"Delete {len(selected_items)} items?\n{label_preview}",
        )
        if not confirm:
            return
        for item in selected_items:
            vals = self.inventory_tree.item(item, 'values')
            if not vals:
                continue
            try:
                self.repo.delete_item(int(vals[0]))
            except Exception:
                pass
        self.view_inventory()

    def clear_inputs(self):
        self.product_name_var.set("")
        self.product_quantity_var.set(0)
        self.product_price_var.set(0.0)
        self.product_category_var.set("")

    def delete_item(self, item_id):
        self.repo.delete_item(item_id)
        self.view_inventory()
        messagebox.showinfo("Deleted", "Item deleted successfully!")