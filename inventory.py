# This file has been modularized into separate components in the app/ directory
# Import the main InventoryManager class from the new modular structure
from app.inventory_manager import InventoryManager

# For backward compatibility, export the main class
__all__ = ['InventoryManager']