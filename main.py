import tkinter as tk
from tkinter import ttk
from ui_components import InventoryApp
from Databases import create_db, create_salesman_db

def main():
    # Initialize main window
    root = tk.Tk()
    root.title("Inventory and Salesman Management")
    root.geometry("800x600")

    # Set up the databases
    create_db()
    create_salesman_db()

    # Create the InventoryApp
    app = InventoryApp(root)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
