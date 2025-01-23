import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from Databases import sync_inventory_with_salesman

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

        # Right Frame: Table for Salesman Details
        tk.Label(right_frame, text="Salesman Details", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)
        columns = ("Product", "Load1", "Load2", "TotalLoad", "Return", "Payment")
        self.details_tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        for col in columns:
            self.details_tree.heading(col, text=col)
            self.details_tree.column(col, anchor="center", width=100)
        self.details_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
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
            cursor.execute("SELECT Distinct name FROM salesman")
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
            # Sync existing inventory products with the new salesman
            sync_inventory_with_salesman(name)

            # Refresh the salesman list
            self.load_salesmen()
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
                SELECT product, load1, load2, totalload, return, payment 
                FROM salesman 
                WHERE name = ?
                """,
                (selected_name,),
            )
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                self.details_tree.insert("", "end", values=row)

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

        new_value = int(new_value)  # Convert the value to integer for calculations

        # Get current row values
        values = list(self.details_tree.item(item_id, "values"))
        values[column_index] = new_value

        # Update TotalLoad (Load1 + Load2) if Load1 or Load2 changes
        if column_index in (1, 2):  # Load1 or Load2
            load1 = int(values[1]) if values[1] else 0
            load2 = int(values[2]) if values[2] else 0
            total_load = load1 + load2
            values[3] = total_load  # Update TotalLoad column

            # Ensure Return is less than TotalLoad
            return_value = int(values[4]) if values[4] else 0
            if return_value >= total_load:
                messagebox.showerror("Validation Error", "Return value must be less than Total Load.")
                entry.destroy()
                return

        # Validate Return if Return column is edited
        if column_index == 4:  # Return
            total_load = int(values[3]) if values[3] else 0
            if new_value >= total_load:
                messagebox.showerror("Validation Error", "Return value must be less than Total Load.")
                entry.destroy()
                return

        # Update the Treeview
        self.details_tree.item(item_id, values=values)
        entry.destroy()

        # Update the database
        try:
            selected_name = self.salesman_list.get(self.salesman_list.curselection())
            product_name = values[0]  # Assuming the first column is "Product"
            conn = sqlite3.connect("salesman.db")
            cursor = conn.cursor()

            # Update the respective column in the database
            if column_index == 1:  # Load1
                cursor.execute(
                    "UPDATE salesman SET load1 = ?, totalload = ? WHERE name = ? AND product = ?",
                    (values[1], values[3], selected_name, product_name),
                )
            elif column_index == 2:  # Load2
                cursor.execute(
                    "UPDATE salesman SET load2 = ?, totalload = ? WHERE name = ? AND product = ?",
                    (values[2], values[3], selected_name, product_name),
                )
            elif column_index == 4:  # Return
                cursor.execute(
                    "UPDATE salesman SET return = ? WHERE name = ? AND product = ?",
                    (values[4], selected_name, product_name),
                )

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Value updated successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
