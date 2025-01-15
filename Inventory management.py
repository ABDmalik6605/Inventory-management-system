import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sqlite3
from datetime import datetime
from fpdf import FPDF

# Database setup for inventory
def create_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            name TEXT,
            quantity INTEGER,
            price_per_kg REAL,
            total_price REAL,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()

# Database setup for salesman
def create_salesman_db():
    conn = sqlite3.connect("salesman.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salesman (
            id INTEGER PRIMARY KEY,
            name TEXT,
            product TEXT,
            quantity INTEGER,
            payment REAL
        )
    """)
    cursor.execute("PRAGMA table_info(salesman)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if "return" not in column_names:
        cursor.execute("ALTER TABLE salesman ADD COLUMN return INTEGER DEFAULT 0")
    conn.commit()
    conn.close()

def generate_salesman_reports():
    # Initialize tkinter (hidden root window for dialog boxes)
    root = tk.Tk()
    root.withdraw()
    # Get the current date and month
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%B")  # Full name of the month (e.g., "January")

    # Base folder for all salesman data
    base_folder = "Salesman Data"

    # Connect to the databases
    conn_salesman = sqlite3.connect("salesman.db")
    cursor_salesman = conn_salesman.cursor()
    conn_inventory = sqlite3.connect("inventory.db")
    cursor_inventory = conn_inventory.cursor()

    # Fetch all salesman data (case-insensitive)
    cursor_salesman.execute("SELECT DISTINCT name FROM salesman")
    salesmen = cursor_salesman.fetchall()

    for salesman in salesmen:
        salesman_name = salesman[0].lower()  # Convert to lowercase for consistent comparison

        # Create the folder path: Salesman Data/salesman_name/current_month
        salesman_folder = os.path.join(base_folder, salesman_name, current_month)
        if not os.path.exists(salesman_folder):
            os.makedirs(salesman_folder)

        # Path to the PDF file for the salesman
        pdf_path = os.path.join(salesman_folder, f"{current_date}.pdf")

        # Create PDF document
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Set title
        pdf.set_font("Arial", size=14, style='B')  # Reduced font size
        pdf.cell(200, 10, txt=f"Sales Report for {salesman_name}", ln=True, align='C')

        # Fetch all products handled by the salesman (case-insensitive comparison)
        cursor_salesman.execute("""
            SELECT product, quantity, payment, return
            FROM salesman
            WHERE LOWER(name) = ?
        """, (salesman_name,))
        transactions = cursor_salesman.fetchall()

        product_data = {}
        for transaction in transactions:
            product, quantity, payment, return_qty = transaction

            # Normalize the product name to lowercase for consistent comparison
            product_normalized = product.lower()

            if product_normalized not in product_data:
                product_data[product_normalized] = {
                    "issues": [],
                    "total_returns": 0,
                    "total_payment": 0
                }

            product_data[product_normalized]["issues"].append(quantity)
            product_data[product_normalized]["total_returns"] += return_qty
            product_data[product_normalized]["total_payment"] += payment
        

        # Generate table in the PDF
        pdf.ln(10)
        pdf.set_font("Arial", size=10, style='B')  # Reduced font size for the table headers

        pdf.cell(35, 8, "Product", border=1, align='C')  # Reduced width
        for i in range(1, len(max(product_data.values(), key=lambda x: len(x["issues"]))["issues"]) + 1):
            pdf.cell(20, 8, f"Issue {i}", border=1, align='C')  # Reduced width
        pdf.cell(20, 8, "T.Issues", border=1, align='C')  # Adjusted width
        pdf.cell(20, 8, "Returns", border=1, align='C')  # Single column for total returns
        pdf.cell(20, 8, "Rate", border=1, align='C')  # Rate column
        pdf.cell(20, 8, "Sales", border=1, align='C')  # Sales column
        pdf.cell(35, 8, "Total Payment", border=1, align='C')
        pdf.ln()

        # Populate table rows
        pdf.set_font("Arial", size=10)  # Reduced font size for the table rows
        for product, details in product_data.items():
            pdf.cell(35, 8, product, border=1, align='C')  # Adjusted width for the Product column

            total_issues = 0
            for issue_qty in details["issues"]:
                total_issues += issue_qty
                pdf.cell(20, 8, str(issue_qty), border=1, align='C')  # Adjusted width for Issue columns

            for _ in range(len(details["issues"]), len(max(product_data.values(), key=lambda x: len(x["issues"]))["issues"])):
                pdf.cell(20, 8, "", border=1, align='C')  # Empty cells for missing issues

            pdf.cell(20, 8, str(total_issues), border=1, align='C')  # Total issues column

            pdf.cell(20, 8, str(details["total_returns"]), border=1, align='C')  # Total returns column

            # Fetch rate from inventory
            cursor_inventory.execute("SELECT price_per_kg FROM inventory WHERE LOWER(name) = LOWER(?)", (product,))
            result = cursor_inventory.fetchone()
            rate = f"Rs.{result[0]:.2f}" if result else "N/A"
            pdf.cell(20, 8, rate, border=1, align='C')  # Rate column

            # Calculate sales
            sales = total_issues - details["total_returns"]
            pdf.cell(20, 8, str(sales), border=1, align='C')  # Sales column

            adjusted_payment = details["total_payment"] if result else 0
            pdf.cell(35, 8, f"Rs.{adjusted_payment:.2f}", border=1, align='C')  # Adjusted width
            pdf.ln()

        try:
            # Save the PDF
            pdf.output(pdf_path)
            print(f"Salesman report for {salesman_name} saved at {pdf_path}")
        except OSError as e:
            error_message = f"Error saving report for {salesman_name} at {pdf_path}: {e}"
            print(error_message)  # Log to console
            messagebox.showerror("File Save Error", error_message)  # Show error dialog


    # Close the database connections
    conn_salesman.close()
    conn_inventory.close()

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory and Salesman Management")
        self.root.geometry("800x600")

        # Database setup
        create_db()
        create_salesman_db()

        # Notebook (tab container)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Inventory tab
        self.inventory_tab = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.inventory_tab, text="Inventory")
        self.setup_inventory_tab()

        # Salesman tab
        self.salesman_tab = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.salesman_tab, text="Salesman")
        self.setup_salesman_tab()

    def setup_inventory_tab(self):
        # Frames for layout
        input_frame = tk.Frame(self.inventory_tab, padx=10, pady=10, bg="#ffffff", relief="groove")
        input_frame.pack(pady=10, fill=tk.X)

        table_frame = tk.Frame(self.inventory_tab, padx=10, pady=10, bg="#ffffff", relief="groove")
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Input fields
        tk.Label(input_frame, text="Product Name", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.product_name_var = tk.StringVar()
        self.product_name_entry = tk.Entry(input_frame, textvariable=self.product_name_var)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Quantity", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5)
        self.product_quantity_var = tk.IntVar()
        self.product_quantity_entry = tk.Entry(input_frame, textvariable=self.product_quantity_var)
        self.product_quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Price per KG", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5)
        self.product_price_var = tk.DoubleVar()
        self.product_price_entry = tk.Entry(input_frame, textvariable=self.product_price_var)
        self.product_price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Category", bg="#ffffff").grid(row=3, column=0, padx=5, pady=5)
        self.product_category_var = tk.StringVar()
        self.product_category_entry = tk.Entry(input_frame, textvariable=self.product_category_var)
        self.product_category_entry.grid(row=3, column=1, padx=5, pady=5)

        # Bind arrow keys for navigation
        self.product_name_entry.bind("<Down>", self.move_to_quantity)
        self.product_quantity_entry.bind("<Up>", self.move_to_product_name)
        self.product_quantity_entry.bind("<Down>", self.move_to_price)
        self.product_price_entry.bind("<Up>", self.move_to_quantity)
        self.product_price_entry.bind("<Down>", self.move_to_category)
        self.product_category_entry.bind("<Up>", self.move_to_price)

        # Buttons
        tk.Button(input_frame, text="Add Product", command=self.add_item, bg="#4caf50", fg="white").grid(row=4, column=0, padx=5, pady=10)
        tk.Button(input_frame, text="View Inventory", command=self.view_inventory, bg="#2196f3", fg="white").grid(row=4, column=1, padx=5, pady=10)

        # Inventory Table
        self.inventory_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Quantity", "Price per KG", "Total Price", "Category"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Name")
        self.inventory_tree.heading("Quantity", text="Quantity")
        self.inventory_tree.heading("Price per KG", text="Price per KG")
        self.inventory_tree.heading("Total Price", text="Total Price")
        self.inventory_tree.heading("Category", text="Category")
        
        for col in ["ID", "Name", "Quantity", "Price per KG", "Total Price", "Category"]:
            self.inventory_tree.column(col, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        self.view_inventory()
        
    #Cursor movements
    def move_to_product_name(self, event=None):
        self.product_name_entry.focus_set()

    def move_to_quantity(self, event=None):
        self.product_quantity_entry.focus_set()

    def move_to_price(self, event=None):
        self.product_price_entry.focus_set()

    def move_to_category(self, event=None):
        self.product_category_entry.focus_set()
        
    #Add inventory
    def add_item(self):
        name = self.product_name_var.get().strip().lower()
        qty = self.product_quantity_var.get()
        price_per_kg = self.product_price_var.get()
        category = self.product_category_var.get().strip().lower()

        if not name or not qty or not price_per_kg:
            messagebox.showwarning("Input Error", "All fields except category are required!")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        # Check if an item with the same name, price, and category exists (case-insensitive)
        cursor.execute("""
            SELECT id, quantity, price_per_kg FROM inventory 
            WHERE LOWER(name) = ? AND price_per_kg = ? AND LOWER(category) = ?
        """, (name, price_per_kg, category))
        existing_item = cursor.fetchone()

        if existing_item:
            # Update quantity and total price of the existing item
            item_id, existing_qty, _ = existing_item
            new_qty = existing_qty + qty
            total_price = new_qty * price_per_kg
            cursor.execute("""
                UPDATE inventory
                SET quantity = ?, total_price = ?
                WHERE id = ?
            """, (new_qty, total_price, item_id))
        else:
            # Add new item
            total_price = qty * price_per_kg
            cursor.execute("""
                INSERT INTO inventory (name, quantity, price_per_kg, total_price, category)
                VALUES (?, ?, ?, ?, ?)
            """, (name, qty, price_per_kg, total_price, category))

        conn.commit()
        conn.close()

        self.clear_inputs()
        self.view_inventory()

    def view_inventory(self):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        conn.close()

        # Clear the tree before inserting
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)

        for row in rows:
            self.inventory_tree.insert("", tk.END, values=row)

        # Bind right-click menu
        self.inventory_tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        item = self.inventory_tree.identify_row(event.y)
        if item:
            self.inventory_tree.selection_set(item)

            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Edit", command=lambda: self.edit_item(item))
            context_menu.add_command(label="Delete", command=lambda: self.delete_item_by_tree(item))
            context_menu.post(event.x_root, event.y_root)

    def edit_item(self, item):
        item_id = self.inventory_tree.item(item, "values")[0]
        current_qty = self.inventory_tree.item(item, "values")[2]
        current_price = self.inventory_tree.item(item, "values")[3]

        # Create a custom dialog for editing
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Item")
        dialog.geometry("300x200")
        dialog.transient(self.root)  # Make it a child of the main window
        dialog.grab_set()  # Make it modal

        # Quantity input
        tk.Label(dialog, text="New Quantity:").pack(pady=5)
        qty_var = tk.IntVar(value=current_qty)
        tk.Entry(dialog, textvariable=qty_var).pack(pady=5)

        # Price per kg input
        tk.Label(dialog, text="New Price per kg:").pack(pady=5)
        price_var = tk.DoubleVar(value=current_price)
        tk.Entry(dialog, textvariable=price_var).pack(pady=5)

        # Buttons
        def save_changes():
            new_qty = qty_var.get()
            new_price_per_kg = price_var.get()
            if new_qty is not None and new_price_per_kg is not None:
                self.update_quantity_and_price(item_id, new_qty, new_price_per_kg)
            dialog.destroy()

        tk.Button(dialog, text="Save", command=save_changes).pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

        dialog.mainloop()

    def update_quantity_and_price(self, item_id, new_qty, new_price_per_kg):
        # Recalculate the total price based on the new values
        total_price = new_qty * new_price_per_kg
        
        # Update the database with the new quantity, price per kg, and total price
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inventory 
            SET quantity = ?, price_per_kg = ?, total_price = ? 
            WHERE id = ?
        """, (new_qty, new_price_per_kg, total_price, item_id))
        conn.commit()
        conn.close()

        self.view_inventory()
        messagebox.showinfo("Updated", "Item updated successfully!")

    def delete_item_by_tree(self, item):
        item_id = self.inventory_tree.item(item, "values")[0]
        self.delete_item(item_id)

    def clear_inputs(self):
        self.product_name_var.set("")
        self.product_quantity_var.set(0)
        self.product_price_var.set(0.0)
        self.product_category_var.set("")

    def delete_item(self, item_id):
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        self.view_inventory()
        messagebox.showinfo("Deleted", "Item deleted successfully!")
            
    def setup_salesman_tab(self):
        # Frames for layout
        input_frame = tk.Frame(self.salesman_tab, padx=10, pady=10, bg="#ffffff", relief="groove")
        input_frame.pack(pady=10, fill=tk.X)

        table_frame = tk.Frame(self.salesman_tab, padx=10, pady=10, bg="#ffffff", relief="groove")
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


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
