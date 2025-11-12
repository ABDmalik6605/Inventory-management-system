import tkinter as tk
from tkinter import ttk

class InventoryUIComponents:
    def __init__(self, parent, inventory_manager):
        self.parent = parent
        self.inventory_manager = inventory_manager
        self.setup_variables()
        
    def setup_variables(self):
        """Initialize all UI variables"""
        self.product_name_var = tk.StringVar()
        # Use StringVar for placeholders and manual parsing
        self.product_quantity_var = tk.StringVar(value="")
        self.product_price_var = tk.StringVar(value="")
        self.product_category_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.total_stock_var = tk.StringVar(value="0.00")
        self.total_sales_var = tk.StringVar(value="0.00")
        # Placeholder texts
        self.quantity_placeholder = "0"
        self.price_placeholder = "0.0"
        
    def create_header_container(self, tab):
        """Create the header container with input fields"""
        # Top container with subtle card style and divider
        header_container = ttk.Frame(tab, padding=(12, 8))
        header_container.pack(padx=12, pady=(10, 6), fill=tk.X)
        header_line = ttk.Separator(tab, orient='horizontal')
        header_line.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        return header_container
        
    def create_input_toolbar(self, header_container):
        """Create the input toolbar with all entry fields"""
        input_frame = ttk.Frame(header_container)
        input_frame.pack(fill=tk.X)
        toolbar_font = ('Segoe UI', 12)

        # Input fields laid out in a single compact row
        ttk.Label(input_frame, text="Item", font=toolbar_font).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="w")
        self.product_name_entry = ttk.Entry(input_frame, textvariable=self.product_name_var, width=24, font=toolbar_font)
        self.product_name_entry.grid(row=0, column=1, padx=(0, 16), pady=4, sticky="ew")

        ttk.Label(input_frame, text="Stock", font=toolbar_font).grid(row=0, column=2, padx=(0, 6), pady=4, sticky="w")
        # Use tk.Entry to support placeholder color
        self.product_quantity_entry = tk.Entry(input_frame, textvariable=self.product_quantity_var, width=8, font=toolbar_font)
        self.product_quantity_entry.grid(row=0, column=3, padx=(0, 16), pady=4, sticky="w")
        self._install_placeholder(self.product_quantity_entry, self.product_quantity_var, self.quantity_placeholder)

        ttk.Label(input_frame, text="Unit Price", font=toolbar_font).grid(row=0, column=4, padx=(0, 6), pady=4, sticky="w")
        self.product_price_entry = tk.Entry(input_frame, textvariable=self.product_price_var, width=10, font=toolbar_font)
        self.product_price_entry.grid(row=0, column=5, padx=(0, 16), pady=4, sticky="w")
        self._install_placeholder(self.product_price_entry, self.product_price_var, self.price_placeholder)

        ttk.Label(input_frame, text="Category", font=toolbar_font).grid(row=0, column=6, padx=(0, 6), pady=4, sticky="w")
        self.product_category_entry = ttk.Entry(input_frame, textvariable=self.product_category_var, width=14, font=toolbar_font)
        self.product_category_entry.grid(row=0, column=7, padx=(0, 16), pady=4, sticky="ew")

        add_button = ttk.Button(input_frame, text="➕ Add", command=self.inventory_manager.add_item, style='Add.TButton')
        add_button.grid(row=0, column=8, padx=(0, 16), pady=2, sticky="w")

        # Search/filter on the far right
        search_group = ttk.Frame(input_frame)
        search_group.grid(row=0, column=9, columnspan=3, sticky='e', padx=(0, 0))
        ttk.Label(search_group, text="Search", font=toolbar_font).grid(row=0, column=0, padx=(0, 6), pady=4, sticky="e")
        self.search_entry = ttk.Entry(search_group, textvariable=self.search_var, width=26, font=toolbar_font)
        self.search_entry.grid(row=0, column=1, padx=(0, 6), pady=4)
        self.search_entry.bind("<KeyRelease>", lambda e: self.inventory_manager.view_inventory(self.search_var.get()))
        search_group.columnconfigure(1, weight=1)

        # Make toolbar responsive: expand Product Name and Category; push Search to the right
        input_frame.columnconfigure(1, weight=2)
        input_frame.columnconfigure(7, weight=1)
        input_frame.columnconfigure(8, weight=0)  # add button
        input_frame.columnconfigure(9, weight=1)  # spacer before search group
        
        return input_frame
        
    def create_table_container(self, tab):
        """Create the table container"""
        table_shell = ttk.Frame(tab, padding=(12, 8))
        table_shell.pack(pady=(0, 12), padx=12, fill=tk.BOTH, expand=True)
        # Subtle table border effect using an inner frame
        table_frame = ttk.Frame(table_shell)
        table_frame.pack(pady=0, padx=8, fill=tk.BOTH, expand=True)
        
        return table_shell, table_frame
        
    def create_footer(self, tab):
        """Create the footer with totals"""
        footer_sep = ttk.Separator(tab, orient='horizontal')
        footer_sep.pack(fill=tk.X, padx=12, pady=(4, 0))
        footer = ttk.Frame(tab, padding=(12, 8))
        footer.pack(fill=tk.X, padx=0, pady=(4, 8))
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=0)
        footer.columnconfigure(2, weight=0)
        
        totals_container = ttk.Frame(footer)
        totals_container.grid(row=0, column=1, sticky='e')
        ttk.Label(totals_container, text="Total Stock Value:", font=('Segoe UI Semibold', 11)).grid(row=0, column=0, padx=(0,6))
        self.total_stock_label = ttk.Label(totals_container, textvariable=self.total_stock_var, font=('Segoe UI', 11))
        self.total_stock_label.grid(row=0, column=1, padx=(0,16))
        ttk.Label(totals_container, text="Total Sales Value:", font=('Segoe UI Semibold', 11)).grid(row=0, column=2, padx=(0,6))
        self.total_sales_label = ttk.Label(totals_container, textvariable=self.total_sales_var, font=('Segoe UI', 11))
        self.total_sales_label.grid(row=0, column=3)
        
        return footer
        
    def clear_inputs(self):
        """Clear all input fields"""
        self.product_name_var.set("")
        self.product_quantity_var.set("")
        self.product_price_var.set("")
        self.product_category_var.set("")
        # Re-apply placeholders immediately
        self._apply_placeholders()

    # --- Placeholder helpers ---
    def _install_placeholder(self, entry, var, placeholder: str):
        """Add placeholder behavior to an Entry using StringVar"""
        # Initial state
        if not var.get():
            try:
                entry.config(fg='#9ca3af')
            except Exception:
                pass
            var.set(placeholder)
        def on_focus_in(event):
            if var.get() == placeholder:
                var.set("")
                try:
                    entry.config(fg='#111827')
                except Exception:
                    pass
            # Select all for quick overwrite
            try:
                entry.after(1, lambda: entry.select_range(0, tk.END))
            except Exception:
                pass
        def on_focus_out(event):
            if var.get().strip() == "":
                var.set(placeholder)
                try:
                    entry.config(fg='#9ca3af')
                except Exception:
                    pass
        def on_ctrl_a(event):
            try:
                entry.select_range(0, tk.END)
            except Exception:
                pass
            return "break"
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Control-a>", on_ctrl_a)

    def _apply_placeholders(self):
        """Reset placeholders on quantity and price if empty."""
        try:
            if self.product_quantity_var.get().strip() == "":
                self.product_quantity_var.set(self.quantity_placeholder)
                self.product_quantity_entry.config(fg='#9ca3af')
        except Exception:
            pass
        try:
            if self.product_price_var.get().strip() == "":
                self.product_price_var.set(self.price_placeholder)
                self.product_price_entry.config(fg='#9ca3af')
        except Exception:
            pass
