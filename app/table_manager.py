import tkinter as tk
from tkinter import ttk, messagebox

class InventoryTableManager:
    def __init__(self, parent, inventory_manager):
        self.parent = parent
        self.inventory_manager = inventory_manager
        self.inventory_tree = None
        self._sold_controls = {}  # row_id -> (minus_label, plus_label)
        self._stock_controls = {}  # row_id -> (minus_label, plus_label)
        self._divider_line = None
        self._divider_glow = None
        self._scrollbar_y = None
        self._scrollbar_x = None
        
    def create_inventory_table(self, table_frame):
        """Create the inventory table with all columns and configuration"""
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
        
        # Configure headers
        headers = ["ID", "Item", "Stock", "Unit Price", "Stock Value", "Category", "Sales", "Sales Value"]
        for header in headers:
            self.inventory_tree.heading(header, text=header)
            self.inventory_tree.column(header, anchor="center")
            
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
        border_top = ttk.Separator(table_frame.master, orient='horizontal')
        border_top.pack(fill=tk.X, pady=(0, 8))

        # Zebra striping for a cleaner look
        self.inventory_tree.tag_configure('oddrow', background='#f9f9f9')
        self.inventory_tree.tag_configure('evenrow', background='#ffffff')
        
        # Setup table functionality
        self._setup_sortable_columns()
        self._setup_table_bindings()
        self._setup_divider()
        
        return self.inventory_tree
        
    def _setup_table_bindings(self):
        """Setup all table event bindings"""
        # Enable inline editing on double-click
        self.inventory_tree.bind('<Double-1>', self._on_tree_double_click)
        # Enable multi-select and bulk delete
        self.inventory_tree.configure(selectmode='extended')
        self.inventory_tree.bind('<Delete>', self._on_delete_selected)
        # Hover cursor hint for editable cells
        self.inventory_tree.bind('<Motion>', self._on_tree_motion_cursor)
        self.inventory_tree.bind('<Leave>', lambda e: self.inventory_tree.configure(cursor=''))
        # Persistent controls for Stock and Sales columns
        self.inventory_tree.bind('<Configure>', lambda e: self.inventory_manager.navigation_manager.position_divider_and_controls(self))
        self.inventory_tree.bind('<<TreeviewSelect>>', lambda e: self.inventory_manager.navigation_manager.position_divider_and_controls(self))
        # Right-click context menu
        self.inventory_tree.bind("<Button-3>", self.inventory_manager.data_operations.show_context_menu)
        
    def _setup_divider(self):
        """Setup the vertical divider between Category and Sales columns"""
        self._divider_line = tk.Frame(self.inventory_tree, bg='#111111', width=2)
        self._divider_line.place_forget()
        self._divider_glow = tk.Frame(self.inventory_tree, bg='#e5e7eb', width=1)
        self._divider_glow.place_forget()
        
    def _setup_sortable_columns(self):
        """Enable sorting by clicking column headers"""
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
            
    def _on_tree_double_click(self, event):
        """Handle double-click editing of table cells"""
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
                    self.inventory_manager.repo.update_name(item_id, new_text)
                    current_values[1] = new_text
                elif field == 'category':
                    self.inventory_manager.repo.update_category(item_id, new_text)
                    current_values[5] = new_text
                elif field == 'quantity':
                    # Treat edited Quantity as remaining stock directly
                    remaining_qty = int(new_text)
                    if remaining_qty < 0:
                        raise ValueError('Quantity cannot be negative')
                    price = float(current_values[3])
                    self.inventory_manager.repo.update_item(item_id, remaining_qty, price)
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
                    self.inventory_manager.repo.update_sold(item_id, sold_qty)
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
                    self.inventory_manager.repo.update_item(item_id, quantity, price)
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
        
    def _on_tree_motion_cursor(self, event):
        """Handle cursor changes on hover for editable cells"""
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
            
    def _on_tree_yscroll(self, *args):
        """Handle vertical scrolling"""
        try:
            self._scrollbar_y.set(*args)
        except Exception:
            pass
        self.inventory_manager.navigation_manager.position_divider_and_controls(self)

    def _on_tree_xscroll(self, *args):
        """Handle horizontal scrolling"""
        try:
            self._scrollbar_x.set(*args)
        except Exception:
            pass
        self.inventory_manager.navigation_manager.position_divider_and_controls(self)
        
    def _on_delete_selected(self, event=None):
        """Handle delete key for selected items"""
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
                self.inventory_manager.repo.delete_item(int(vals[0]))
            except Exception:
                pass
        self.inventory_manager.view_inventory()
