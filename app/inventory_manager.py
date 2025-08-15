import tkinter as tk
from tkinter import ttk
from .ui_components import InventoryUIComponents
from .table_manager import InventoryTableManager
from .navigation_manager import InventoryNavigationManager
from .data_operations import InventoryDataOperations
from .inventory_repository import InventoryRepository

class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.repo = InventoryRepository()
        
        # Initialize all component managers
        self.ui_components = None
        self.table_manager = None
        self.navigation_manager = InventoryNavigationManager(self)
        self.data_operations = InventoryDataOperations(self)

    def create_inventory_tab(self, container):
        """Create content area inside the provided container (no tabs)"""
        inventory_view = ttk.Frame(container)
        inventory_view.pack(fill=tk.BOTH, expand=True)
        self.setup_inventory_tab(inventory_view)
        return inventory_view

    def setup_inventory_tab(self, tab):
        """Setup the complete inventory tab with all components"""
        # Initialize UI components
        self.ui_components = InventoryUIComponents(self.root, self)
        
        # Create header container and input toolbar
        header_container = self.ui_components.create_header_container(tab)
        input_frame = self.ui_components.create_input_toolbar(header_container)
        
        # Setup keyboard navigation
        self.navigation_manager.setup_keyboard_navigation(self.ui_components)
        
        # Create table container and table
        table_shell, table_frame = self.ui_components.create_table_container(tab)
        self.table_manager = InventoryTableManager(self.root, self)
        self.inventory_tree = self.table_manager.create_inventory_table(table_frame)
        
        # Create footer
        footer = self.ui_components.create_footer(tab)
        
        # Initial data load
        self.view_inventory()
        
    def add_item(self):
        """Add item - delegate to data operations"""
        self.data_operations.add_item()
        
    def view_inventory(self, search_query: str = ""):
        """View inventory - delegate to data operations"""
        self.data_operations.view_inventory(search_query)
        
    def delete_item(self, item_id):
        """Delete item - delegate to data operations"""
        self.data_operations.delete_item(item_id)
        
    def delete_item_by_tree(self, item):
        """Delete item by tree - delegate to data operations"""
        self.data_operations.delete_item_by_tree(item)
        
    def update_quantity_and_price(self, item_id, new_qty, new_price_per_kg):
        """Update quantity and price - delegate to data operations"""
        self.data_operations.update_quantity_and_price(item_id, new_qty, new_price_per_kg)
        
    def show_context_menu(self, event):
        """Show context menu - delegate to data operations"""
        self.data_operations.show_context_menu(event)
        
    def clear_inputs(self):
        """Clear inputs - delegate to UI components"""
        self.ui_components.clear_inputs()
