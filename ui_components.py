import tkinter as tk
from tkinter import ttk, messagebox
from inventory import InventoryManager
from salesman import SalesmanManager

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory and Salesman Management")
        self.root.geometry("800x600")

        # Create InventoryManager and SalesmanManager instances
        self.inventory_manager = InventoryManager(self.root)
        self.salesman_manager = SalesmanManager(self.root)

        # Set up tabs for Inventory and Salesman
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.inventory_tab = self.inventory_manager.create_inventory_tab(self.notebook)
        self.salesman_tab = self.salesman_manager.create_salesman_tab(self.notebook)
