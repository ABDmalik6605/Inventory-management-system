import tkinter as tk
from tkinter import ttk, messagebox
from app.inventory_manager import InventoryManager

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management")
        self.root.geometry("1100x700")

        # Create InventoryManager instance
        self.inventory_manager = InventoryManager(self.root)

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

        # Replace top tabs with a single content container
        content = ttk.Frame(root)
        content.pack(fill=tk.BOTH, expand=True)
        self.inventory_manager.create_inventory_tab(content)
