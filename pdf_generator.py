import os
import sqlite3
from datetime import datetime
from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox

def generate_salesman_reports(selected_name):
    # Prepare the directory path
    current_month = datetime.now().strftime("%B")
    current_date = datetime.now().strftime("%Y-%m-%d")
    directory_path = os.path.join("SalesmanData", selected_name, current_month)

    # Ensure the directory exists
    os.makedirs(directory_path, exist_ok=True)

    # Prepare the PDF file path
    pdf_path = os.path.join(directory_path, f"{current_date}.pdf")

    # Check if the file is open by trying to open it in write mode
    try:
        with open(pdf_path, 'x'):  # Try to create the file
            pass
    except FileExistsError:
        # If the file already exists, check if it's currently open
        try:
            # Try to open the file in append mode to see if it is locked (i.e., open)
            with open(pdf_path, 'a'):
                pass
        except IOError:
            messagebox.showerror("File Open", f"The file '{pdf_path}' is currently open. Please close it before saving.")
            return  # Exit the function if the file is open

    # Initialize FPDF object
    pdf = FPDF()
    pdf.add_page()

    # Set font for the PDF
    pdf.set_font("Arial", size=12)

    # Add title
    pdf.cell(200, 10, txt=f"Salesman Details for {selected_name}", ln=True, align="C")
    pdf.ln(10)

    # Query total payment for the selected salesman
    try:
        conn = sqlite3.connect("salesman.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(payment) FROM salesman WHERE name = ?",
            (selected_name,)
        )
        total_payment = cursor.fetchone()[0] or 0.0
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return

    # Add total payment to the PDF with Rs
    pdf.cell(200, 10, txt=f"Total Payment: Rs {total_payment:.2f}", ln=True, align="C")
    pdf.ln(10)
    
    # Query Expense for the selected salesman
    try:
        conn = sqlite3.connect("salesman.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Distinct Expense FROM salesman WHERE name = ?",
            (selected_name,)
        )
        expense = cursor.fetchone()[0] or 0.0
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return

    # Add total payment to the PDF with Rs
    pdf.cell(200, 10, txt=f"Expense : Rs {expense:.2f}", ln=True, align="C")
    pdf.ln(5)

    # Set a smaller left margin to accommodate the table
    pdf.set_left_margin(10)
    
    # Table headers with an additional 'Rate' column
    columns = ("Product", "Load1", "Load2", "TotalLoad", "Return", "Sales", "Rate", "Payment")
    

    # Adjust column widths to fit the page
    column_widths = [27, 20, 20, 25, 20, 20, 28, 30]

    for col, width in zip(columns, column_widths):
        pdf.cell(width, 10, txt=col, border=1, align="C")
    pdf.ln()

    # Fetch salesman data and inventory data for PDF
    try:
        conn = sqlite3.connect("salesman.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT product, load1, load2, load1+load2 AS totalload, return, load1+load2-return AS sales, payment
            FROM salesman 
            WHERE name = ? 
            """,
            (selected_name,)
        )
        rows = cursor.fetchall()

        # Write data to the PDF
        for row in rows:
            product = row[0]
            # Fetch price per kg for the current product from the inventory
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT price_per_kg FROM inventory WHERE name = ?",
                (product,)
            )
            price_per_kg = cursor.fetchone()
            rate = price_per_kg[0] if price_per_kg else 0.0  # Default to 0.0 if no price is found

            # Add product data to the table, including the rate and payment with Rs
            row_data = list(row)  # Convert tuple to list to modify it
            row_data.insert(6, f"Rs {rate:.2f}")  # Insert rate with Rs
            row_data.insert(7,f"Rs {row_data[7]:.2f}")  # Append payment with Rs
            
            # Add each item to the PDF table
            for item, width in zip(row_data, column_widths):
                pdf.cell(width, 10, txt=str(item), border=1, align="C")
            pdf.ln()

        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return

    # Output the PDF to the specified path
    pdf.output(pdf_path)

    return pdf_path
