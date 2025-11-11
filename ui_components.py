import tkinter as tk
from tkinter import ttk, messagebox
from app.inventory_manager import InventoryManager
from app.receipt_manager import ReceiptManager

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1200x750")

        # Create manager instances
        self.inventory_manager = InventoryManager(self.root)
        # Pass reference so sales can trigger inventory refresh on receipt generation
        self.receipt_manager = ReceiptManager(self.root, inventory_manager_ref=self.inventory_manager)

        # Global ttk styling for a clean, modern look
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        # Base colors (replace any brown with blue/gray scheme)
        bg_app = '#f5f7fb'
        accent = '#2563eb'  # blue
        accent_active = '#1d4ed8'
        secondary = '#6b7280'  # gray

        self.root.configure(bg=bg_app)
        style.configure('TFrame', background=bg_app)
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 11), borderwidth=0,
                        background='#ffffff', fieldbackground='#ffffff')
        style.map('Treeview', background=[('selected', '#dbeafe')],
                   foreground=[('selected', '#111827')])
        style.configure('Treeview.Heading', font=('Segoe UI Semibold', 11),
                        background='#eef2f7', foreground='#111827')
        style.map('Treeview.Heading', background=[('active', '#e5e7eb')])
        style.configure('TSeparator', background='#e5e7eb')
        style.configure('TButton', font=('Segoe UI', 11), relief='flat')
        style.configure('TLabel', font=('Segoe UI', 11), background=bg_app)

        # Accent and secondary button styles with hover/active effects
        # Slightly smaller add button padding
        style.configure('Add.TButton', background=accent, foreground='white', padding=(10, 5))
        style.map('Add.TButton', background=[('active', accent_active), ('pressed', accent_active)])
        style.configure('Search.TButton', background=secondary, foreground='white', padding=(12, 6))
        style.map('Search.TButton', background=[('active', '#4b5563'), ('pressed', '#4b5563')])
        style.configure('Outline.TButton', background=bg_app, foreground=secondary, padding=(10, 6))

        # Configure tab style
        style.configure('TNotebook', background=bg_app, borderwidth=0)
        style.configure('TNotebook.Tab', font=('Segoe UI', 11), padding=(20, 10))
        style.map('TNotebook.Tab', 
                  background=[('selected', accent), ('!selected', '#e5e7eb')],
                  foreground=[('selected', 'white'), ('!selected', '#374151')])

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        inventory_tab = ttk.Frame(self.notebook)
        sales_tab = ttk.Frame(self.notebook)
        invoices_tab = ttk.Frame(self.notebook)

        self.notebook.add(inventory_tab, text='📦 Inventory')
        self.notebook.add(sales_tab, text='💰 Sales')
        self.notebook.add(invoices_tab, text='📋 Invoices')

        # Setup each tab
        self.inventory_manager.create_inventory_tab(inventory_tab)
        self.receipt_manager.create_receipt_tab(sales_tab)
        self.receipt_manager.create_invoices_tab(invoices_tab)
