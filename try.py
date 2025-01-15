import os
import sqlite3
from datetime import datetime
from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox

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

        # # Process product data
        # product_data = {}
        # for transaction in transactions:
        #     product, quantity, payment, return_qty = transaction

        #     if product not in product_data:
        #         product_data[product] = {
        #             "issues": [],
        #             "total_returns": 0,
        #             "total_payment": 0
        #         }

        #     product_data[product]["issues"].append(quantity)
        #     product_data[product]["total_returns"] += return_qty
        #     product_data[product]["total_payment"] += payment
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

generate_salesman_reports()
