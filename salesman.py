import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pdf_generator import generate_salesman_reports

class SalesmanManager:
    def __init__(self, root):
        self.root = root

    def create_salesman_tab(self, notebook):
        salesman_tab = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(salesman_tab, text="Salesman")
        self.setup_salesman_tab(salesman_tab)
        return salesman_tab

    # def setup_salesman_tab(self, tab):
    #     input_frame = tk.Frame(tab, padx=10, pady=10, bg="#ffffff", relief="groove")
    #     input_frame.pack(pady=10, fill=tk.X)

    #     # Define input fields, buttons, and table for the Salesman tab
    #     pass

    # def add_salesman(self):
    #     # Logic to add a salesman
    #     pass

    # # Other methods related to salesman operations
    def setup_salesman_tab(self,tab):
        # Frames for layout
        input_frame = tk.Frame(tab,padx=10, pady=10, bg="#ffffff", relief="groove")
        input_frame.pack(pady=10, fill=tk.X)

        table_frame = tk.Frame(tab,padx=10, pady=10, bg="#ffffff", relief="groove")
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Input fields
        tk.Label(input_frame, text="Salesman Name", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.salesman_name_var = tk.StringVar()
        self.salesman_name_entry = tk.Entry(input_frame, textvariable=self.salesman_name_var)
        self.salesman_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Product Name", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5)
        self.salesman_product_var = tk.StringVar()
        self.salesman_product_entry = tk.Entry(input_frame, textvariable=self.salesman_product_var)
        self.salesman_product_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Quantity", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5)
        self.salesman_quantity_var = tk.IntVar()
        self.salesman_quantity_entry = tk.Entry(input_frame, textvariable=self.salesman_quantity_var)
        self.salesman_quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        # Bind arrow keys for navigation
        self.salesman_name_entry.bind("<Down>", self.move_to_product_field)
        self.salesman_product_entry.bind("<Up>", self.move_to_salesman_name_field)
        self.salesman_product_entry.bind("<Down>", self.move_to_quantity_field)
        self.salesman_quantity_entry.bind("<Up>", self.move_to_product_field)
        
        # Buttons
        tk.Button(input_frame, text="Add Salesman", command=self.add_salesman, bg="#4caf50", fg="white").grid(row=3, column=0, padx=5, pady=10)
        tk.Button(input_frame, text="View Salesmen", command=self.view_salesmen, bg="#2196f3", fg="white").grid(row=3, column=1, padx=5, pady=10)
        tk.Button(input_frame, text="Save Salesmen data", command=generate_salesman_reports, bg="#FF0000", fg="white").grid(row=3, column=2, padx=15, pady=10)
        tk.Button(input_frame, text="Clear Record", command=self.erase_all_data, bg="#000000", fg="white").grid(row=3, column=3, padx=15, pady=10)
        
        # Salesman Table
        self.salesman_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Product", "Quantity", "Payment","Return"), show="headings")
        self.salesman_tree.heading("ID", text="ID")
        self.salesman_tree.heading("Name", text="Name")
        self.salesman_tree.heading("Product", text="Product")
        self.salesman_tree.heading("Quantity", text="Quantity")
        self.salesman_tree.heading("Payment", text="Payment")
        self.salesman_tree.heading("Return", text="Return")

        # Align columns to the center
        for col in ["ID", "Name", "Product", "Quantity", "Payment", "Return"]:
            self.salesman_tree.column(col, anchor="center")

        # Add scrollbar for the treeview
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.salesman_tree.yview)
        self.salesman_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack the treeview to display the table
        self.salesman_tree.pack(fill=tk.BOTH, expand=True)

        # Bind the double-click event for editing a salesman entry
        self.salesman_tree.bind("<Double-1>", self.edit_salesman)
        self.view_salesmen()
        
    #Cursor movements
    def move_to_salesman_name_field(self, event=None):
        self.salesman_name_entry.focus_set()

    def move_to_product_field(self, event=None):
        self.salesman_product_entry.focus_set()

    def move_to_quantity_field(self, event=None):
        self.salesman_quantity_entry.focus_set()
        
    #Add salesman
    def add_salesman(self):
        name = self.salesman_name_var.get().strip()
        product = self.salesman_product_var.get().strip()
        quantity = self.salesman_quantity_var.get()

        if not name or not product or not quantity:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        # Check if the product exists in the inventory database (case-insensitive)
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, quantity, price_per_kg FROM inventory WHERE LOWER(name) = LOWER(?)", (product,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            messagebox.showwarning("Product Error", f"The product '{product}' does not exist in the inventory!")
            return

        # Extract the product data from the query result
        product_id, product_name, inventory_quantity, price_per_kg = result

        # Check if the entered quantity is greater than available quantity
        if quantity > inventory_quantity:
            conn.close()
            messagebox.showwarning("Quantity Error", f"Entered quantity ({quantity}) exceeds available quantity ({inventory_quantity}) in the inventory!")
            return

        # Subtract the quantity from the inventory
        new_quantity = inventory_quantity - quantity
        total_price = new_quantity * price_per_kg

        # Update the inventory with the new quantity and total price
        cursor.execute("UPDATE inventory SET quantity = ?, total_price = ? WHERE id = ?", (new_quantity, total_price, product_id))
        conn.commit()

        # Calculate the payment (quantity * price_per_kg)
        payment = quantity * price_per_kg

        # Add the salesman record to the salesman table, including the calculated payment
        conn = sqlite3.connect("salesman.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO salesman (name, product, quantity, payment) VALUES (?, ?, ?, ?)", (name, product, quantity, payment))
        conn.commit()
        conn.close()

        # Clear fields and refresh salesmen view
        self.salesman_name_var.set("")
        self.salesman_product_var.set("")
        self.salesman_quantity_var.set(0)
        self.view_salesmen()
        generate_salesman_reports()


    def view_salesmen(self):
        conn = sqlite3.connect("salesman.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM salesman")
        rows = cursor.fetchall()
        conn.close()

        for row in self.salesman_tree.get_children():
            self.salesman_tree.delete(row)

        for row in rows:
            self.salesman_tree.insert("", tk.END, values=row)

    def erase_all_data(self):
        # Show a confirmation dialog
        response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete all data?")
        
        # If the user clicks "Yes", proceed with deletion
        if response:
            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM salesman")  # Deletes all rows from the table
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "All data has been deleted.")
        else:
            messagebox.showinfo("Cancelled", "Data deletion has been cancelled.")
            
        self.view_salesmen()


    def edit_salesman(self, event):
        selected_item = self.salesman_tree.selection()
        if not selected_item:
            return

        item = self.salesman_tree.item(selected_item)
        record = item["values"]
        
        # Variables for current quantity and product name
        current_quantity = record[3]
        product = record[2]

        self.salesman_return_var = tk.IntVar(value=0)  # New variable for "return"

        def save_changes():
            return_value = self.salesman_return_var.get()

            if return_value <= 0:
                messagebox.showwarning("Input Error", "Return quantity must be greater than 0!")
                return

            if return_value > current_quantity:
                messagebox.showwarning("Input Error", "Return quantity cannot be greater than the current quantity!")
                return

            # Fetch price_per_kg from the inventory database
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute("SELECT quantity, price_per_kg FROM inventory WHERE LOWER(name) = LOWER(?)", (product,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                messagebox.showwarning("Product Error", f"The product '{product}' does not exist in the inventory!")
                return

            inventory_quantity, price_per_kg = result

            # Update the inventory with the returned quantity
            new_inventory_quantity = inventory_quantity + return_value
            total_price = new_inventory_quantity * price_per_kg

            cursor.execute("UPDATE inventory SET quantity=?, total_price=? WHERE LOWER(name) = LOWER(?)",
                        (new_inventory_quantity, total_price, product))
            conn.commit()
            conn.close()

            # Update the salesman's record with the new quantity and payment
            new_salesman_quantity = current_quantity #- return_value
            payment = (new_salesman_quantity - return_value )* price_per_kg  # Recalculate payment

            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE salesman SET quantity=?, payment=?, return=? WHERE id=?",
                        (new_salesman_quantity, payment, return_value, record[0]))
            conn.commit()
            conn.close()
            generate_salesman_reports()

            self.view_salesmen()
            top.destroy()

        # Create a new top-level window to ask for the return quantity
        top = tk.Toplevel(self.root)
        top.title("Enter Return Quantity")

        tk.Label(top, text=f"Product: {product}").grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(top, text=f"Current Quantity: {current_quantity}").grid(row=1, column=0, padx=10, pady=10, columnspan=2)

        tk.Label(top, text="Return Quantity").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(top, textvariable=self.salesman_return_var).grid(row=2, column=1, padx=10, pady=10)

        tk.Button(top, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)
