import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from Databases import sync_inventory_with_salesman
from pdf_generator import generate_salesman_reports

class SalesmanManager:
    def __init__(self, root):
        self.root = root

    def create_salesman_tab(self, notebook):
        # Create the tab frame
        salesman_tab = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(salesman_tab, text="Salesmen")

        # Create two frames for the split screen
        left_frame = tk.Frame(salesman_tab, bg="#f0f0f0", width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        right_frame = tk.Frame(salesman_tab, bg="#ffffff")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Left Frame: List of Salesmen
        tk.Label(left_frame, text="Salesmen", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        self.salesman_list = tk.Listbox(left_frame, font=("Arial", 12))
        self.salesman_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add event to update the right table when a salesman is selected
        self.salesman_list.bind("<<ListboxSelect>>", lambda e: self.show_salesman_details(right_frame))

        # Add New Salesman Section
        add_frame = tk.Frame(left_frame, bg="#f0f0f0")
        add_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(add_frame, text="Add Salesman:", font=("Arial", 12), bg="#f0f0f0").pack(anchor=tk.W)
        self.new_salesman_entry = tk.Entry(add_frame, font=("Arial", 12))
        self.new_salesman_entry.pack(fill=tk.X, pady=5)

        add_button = tk.Button(add_frame, text="Add", font=("Arial", 12), bg="#4CAF50", fg="white",
                               command=self.add_salesman)
        add_button.pack(pady=5)
        
        # Add New Expense Section
        expense_frame = tk.Frame(right_frame, bg="#ffffff")
        expense_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(expense_frame, text="Add Expense:", font=("Arial", 12), bg="#ffffff").pack(anchor=tk.W)
        self.new_expense_entry = tk.Entry(expense_frame, font=("Arial", 12))
        self.new_expense_entry.pack(fill=tk.X, pady=5)

        add_expense_button = tk.Button(
            expense_frame, text="Add Expense", font=("Arial", 12), bg="#4CAF50", fg="white",
            command=self.add_expense
        )
        add_expense_button.pack(pady=5)

        # Delete Salesman Button
        delete_button = tk.Button(
            left_frame,
            text="Delete Salesman",
            font=("Arial", 12),
            bg="#f44336",
            fg="white",
            command=self.delete_salesman
        )
        delete_button.pack(pady=5)

        # Right Frame: Table for Salesman Details
        tk.Label(right_frame, text="Salesman Details", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)
        columns = ("Product", "Load1", "Load2", "TotalLoad", "Return", "Sales", "Payment")
        self.details_tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        for col in columns:
            self.details_tree.heading(col, text=col)
            self.details_tree.column(col, anchor="center", width=100)
        self.details_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add a label for displaying Total Payment
        self.total_payment_label = tk.Label(right_frame, text="Total Payment: 0.00", font=("Arial", 14, "bold"), bg="#ffffff")
        self.total_payment_label.pack(pady=10)

        # Save button to generate PDF
        self.save_button = tk.Button(right_frame, text="Save", font=("Arial", 12), bg="#4CAF50", fg="white", command=self.save_salesman_data)
        self.save_button.pack(pady=5)

        # Clear Record button
        clear_record_button = tk.Button(right_frame,text="Clear Records",font=("Arial", 12),bg="#f44336",fg="white",command=self.clear_records)
        clear_record_button.pack(pady=5)
        # Enable cell editing feature
        self.enable_cell_editing()
        # Load data into the left listbox
        self.load_salesmen()

        return salesman_tab

    def load_salesmen(self):
        # Connect to the database and fetch salesman names
        try:
            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM salesman")
            rows = cursor.fetchall()
            conn.close()

            # Populate the Listbox with salesman names
            self.salesman_list.delete(0, tk.END)
            for row in rows:
                self.salesman_list.insert(tk.END, row[0])

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def add_salesman(self):
        # Get the name from the entry field
        name = self.new_salesman_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Salesman name cannot be empty.")
            return

        # Ensure the name is a string
        if not isinstance(name, str):
            raise ValueError(f"Expected 'name' to be a string, but got {type(name).__name__}")

        try:
            # Check if the salesman already exists (case-insensitive)
            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM salesman WHERE LOWER(name) = LOWER(?)", (name,))
            existing_salesman = cursor.fetchone()

            if existing_salesman:
                messagebox.showerror("Duplicate Error", f"Salesman '{name}' already exists.")
                conn.close()
                return

            # Sync existing inventory products with the new salesman
            sync_inventory_with_salesman(name)

            # Refresh the salesman list
            self.load_salesmen()
            conn.close()

            messagebox.showinfo("Success", f"Salesman '{name}' added successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def show_salesman_details(self, right_frame):
        # Clear the current details in the table
        self.details_tree.delete(*self.details_tree.get_children())

        # Get the selected salesman name
        selected_index = self.salesman_list.curselection()
        if not selected_index:
            return  # No selection, exit the function

        selected_name = self.salesman_list.get(selected_index)

        # Fetch and display the details of the selected salesman
        try:
            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT product, load1, load2, load1+load2 AS totalload, return, load1+load2-return AS sales, payment 
                FROM salesman 
                WHERE name = ?
                """,
                (selected_name,),
            )
            rows = cursor.fetchall()

            # Display data in the table
            for row in rows:
                self.details_tree.insert("", "end", values=row)

            # Calculate and display total payment
            cursor.execute(
                "SELECT SUM(payment) FROM salesman WHERE name = ?", (selected_name,)
            )
            total_payment = cursor.fetchone()[0] or 0.0
            self.total_payment_label.config(text=f"Total Payment: {total_payment:.2f}")

            conn.close()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def delete_salesman(self):
        # Get the selected salesman name
        selected_index = self.salesman_list.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a salesman to delete.")
            return

        selected_name = self.salesman_list.get(selected_index)

        # Confirm the deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete salesman '{selected_name}'?"
        )
        if not confirm:
            return

        # Delete the salesman from the database
        try:
            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()

            # Remove the salesman from the database
            cursor.execute("DELETE FROM salesman WHERE name = ?", (selected_name,))
            conn.commit()
            conn.close()

            # Refresh the salesmen list
            self.load_salesmen()

            # Clear the details table
            self.details_tree.delete(*self.details_tree.get_children())

            # Reset the total payment label
            self.total_payment_label.config(text="Total Payment: 0.00")

            messagebox.showinfo("Success", f"Salesman '{selected_name}' deleted successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def save_salesman_data(self):
        # Get the selected salesman name
        selected_index = self.salesman_list.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a salesman first.")
            return

        selected_name = self.salesman_list.get(selected_index)

        # Call the utility function to save data to PDF
        pdf_path = generate_salesman_reports(selected_name)

        # Notify the user that the PDF has been saved
        if pdf_path:
            print("PDF Saved", f"Salesman data has been saved to {pdf_path}")
            
    def clear_records(self):
        # Save data for all salesmen
        try:
            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()

            # Fetch all salesmen names
            cursor.execute("SELECT DISTINCT name FROM salesman")
            salesmen = cursor.fetchall()

            # Call save_salesman_data for each salesman
            for salesman in salesmen:
                self.save_salesman_data()

            # Reset values to 0 for all salesmen
            cursor.execute("""
                UPDATE salesman
                SET load1 = 0, load2 = 0, return = 0, payment = 0, expense = 0
            """)
            conn.commit()
            conn.close()

            # Reload the list of salesmen to refresh UI
            self.load_salesmen()
            messagebox.showinfo("Success", "Records cleared successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def add_expense(self):
        # Get the selected salesman name
        selected_index = self.salesman_list.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a salesman first.")
            return

        selected_name = self.salesman_list.get(selected_index)
        
        # Get the expense amount from the entry field
        try:
            expense = float(self.new_expense_entry.get().strip())
            if expense <= 0:
                raise ValueError("Expense must be a positive number.")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid expense value: {e}")
            return

        # Insert the expense into the database
        try:
            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()
            cursor.execute(
            "UPDATE salesman SET expense = ? WHERE name = ?",
            (expense, selected_name)
            )
            conn.commit()
            conn.close()

            # Update the total expense and refresh the table
            self.show_salesman_details(None)
            messagebox.showinfo("Success", "Expense added successfully!")
            self.save_salesman_data()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def enable_cell_editing(self):
        self.details_tree.bind("<Double-1>", self.on_cell_double_click)

    def on_cell_double_click(self, event):
        # Get the selected row and column
        item_id = self.details_tree.identify_row(event.y)
        column_id = self.details_tree.identify_column(event.x)

        if not item_id or column_id not in ("#2", "#3", "#5"):  # Edit only "Load1", "Load2", and "Return"
            return

        # Get the cell value
        column_index = int(column_id.strip("#")) - 1
        cell_value = self.details_tree.item(item_id, "values")[column_index]

        # Get the cell coordinates
        x, y, width, height = self.details_tree.bbox(item_id, column_id)

        # Create an Entry widget for editing
        entry = tk.Entry(self.details_tree, font=("Arial", 12))
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, cell_value)

        # Add focus-out and Enter key events to save changes
        entry.bind("<Return>", lambda e: self.save_cell_value(item_id, column_index, entry))
        entry.bind("<FocusOut>", lambda e: entry.destroy())

        entry.focus()


    def save_cell_value(self, item_id, column_index, entry):
        # Get the new value from the Entry widget
        new_value = entry.get().strip()
        if not new_value.isdigit() or int(new_value) < 0:  # Check for non-negative numeric values
            messagebox.showerror("Input Error", "Only non-negative numeric values are allowed.")
            entry.destroy()
            return

        new_value = int(new_value)  # Convert the value to an integer for calculations

        # Get current row values
        values = list(self.details_tree.item(item_id, "values"))

        # Initialize total_load and sales
        load1 = int(values[1]) if values[1] else 0
        load2 = int(values[2]) if values[2] else 0
        return_value = int(values[4]) if values[4] else 0
        total_load = load1 + load2
        sales = total_load - return_value

        # Update the specific column value
        values[column_index] = new_value

        # Get the product name
        product_name = values[0]  # Assuming the first column is "Product"

        # Fetch inventory data
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT quantity, price_per_kg FROM inventory WHERE name = ?", (product_name,))
        inventory_data = cursor.fetchone()
        conn.close()

        if not inventory_data:
            messagebox.showerror("Inventory Error", f"Product '{product_name}' not found in inventory.")
            entry.destroy()
            return

        available_quantity, price_per_kg = inventory_data

        # Handle different columns
        if column_index in (1, 2):  # If Load1 or Load2 is edited
            required_quantity = new_value - (load1 if column_index == 1 else load2)

            if required_quantity > available_quantity:
                messagebox.showerror("Inventory Error", f"Insufficient quantity for '{product_name}' in inventory.")
                entry.destroy()
                return

            # Update inventory
            new_inventory_quantity = available_quantity - required_quantity
            new_total_price = new_inventory_quantity * price_per_kg

            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE inventory SET quantity = ?, total_price = ? WHERE name = ?",
                (new_inventory_quantity, new_total_price, product_name),
            )
            conn.commit()
            conn.close()

            # Update the salesman's data
            if column_index == 1:
                load1 = new_value
            else:
                load2 = new_value

            total_load = load1 + load2
            values[3] = total_load  # Update TotalLoad

            if return_value >= total_load:
                messagebox.showerror("Validation Error", "Return value must be less than Total Load.")
                entry.destroy()
                return

            sales = total_load - return_value
            values[5] = sales  # Update Sales

        elif column_index == 4:  # If Return is edited
            return_value = new_value
            if return_value >= total_load:
                messagebox.showerror("Validation Error", "Return value must be less than Total Load.")
                entry.destroy()
                return

            # Update inventory with returned quantity
            new_inventory_quantity = available_quantity + return_value
            new_total_price = new_inventory_quantity * price_per_kg

            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE inventory SET quantity = ?, total_price = ? WHERE name = ?",
                (new_inventory_quantity, new_total_price, product_name),
            )
            conn.commit()
            conn.close()

            sales = total_load - return_value
            values[5] = sales  # Update Sales
            values[4] = return_value  # Update Return value in Treeview

        # Calculate payment
        payment = sales * price_per_kg
        values[6] = payment  # Assuming column 6 in Treeview is for Payment

        # Update the Treeview
        self.details_tree.item(item_id, values=values)
        entry.destroy()

        # Update the database
        try:
            selected_name = self.salesman_list.get(self.salesman_list.curselection())

            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()

            if column_index == 1:  # Update Load1
                cursor.execute(
                    "UPDATE salesman SET load1 = ?, payment = ? WHERE name = ? AND product = ?",
                    (values[1], payment, selected_name, product_name),
                )
            elif column_index == 2:  # Update Load2
                cursor.execute(
                    "UPDATE salesman SET load2 = ?, payment = ? WHERE name = ? AND product = ?",
                    (values[2], payment, selected_name, product_name),
                )
            elif column_index == 4:  # Update Return
                cursor.execute(
                    "UPDATE salesman SET return = ?, payment = ? WHERE name = ? AND product = ?",
                    (values[4], payment, selected_name, product_name),
                )

            conn.commit()
            cursor.execute(
                "SELECT SUM(payment) FROM salesman WHERE name = ?", (selected_name,)
            )
            total_payment = cursor.fetchone()[0] or 0.0
            self.total_payment_label.config(text=f"Total Payment: {total_payment:.2f}")

            conn.close()
            messagebox.showinfo("Success", "Value updated successfully!")
            self.save_salesman_data()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
