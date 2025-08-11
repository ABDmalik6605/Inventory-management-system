import tkinter as tk
from tkinter import ttk
from ui_components import InventoryApp
from app.db import init_db

def main():
    # Initialize main window
    root = tk.Tk()
    root.title("Inventory Management")
    root.geometry("800x600")

    # Set up the database
    init_db()

    # Create the InventoryApp
    app = InventoryApp(root)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
