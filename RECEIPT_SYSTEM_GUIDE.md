# Receipt Generation System Guide

## Overview
The Receipt Generation System is a comprehensive feature added to the Inventory Management System that allows you to:
- Create professional receipts for customer purchases
- Track sales with unique invoice numbers
- Manage multiple items per receipt
- View and reprint past receipts
- Automatically update inventory when sales are made

## Features

### 1. **Generate Receipts**
- Add multiple products to a shopping cart
- Enter product ID and quantity
- Set custom selling prices
- Generate professional receipts with invoice numbers

### 2. **Professional Receipt Format**
Each receipt includes:
- **Company Information** (customizable in `receipt_generator.py`)
- **Unique Invoice Number** (format: INV-YYYYMMDD-XXXX)
- **Date & Time** of purchase
- **Customer Name** (default: "Walk-in Customer")
- **Product Details**: Name, Quantity, Price per Unit, Total
- **Subtotal, Tax (if applicable), and Grand Total**
- **Professional formatting** with clear sections

### 3. **Inventory Integration**
- Automatically reduces stock when receipt is generated
- Validates stock availability before sale
- Updates purchase records for profit tracking
- Restores stock if receipt is deleted

### 4. **Receipt Management**
- View all generated receipts
- Search and filter receipts
- Reprint any past receipt
- Delete receipts (with stock restoration)
- Double-click to view receipt details

## How to Use

### Generating a Receipt

1. **Open the Receipt Generation Tab**
   - Click on the "🧾 Receipt Generation" tab in the application

2. **Add Products to Cart**
   - Enter the **Product ID** (from your inventory)
   - Click **"🔍 Fetch Details"** to load product information
   - The system will automatically display:
     - Product Name
     - Available Stock
     - Suggested Price (stock price)
   - Enter the **Quantity** you want to sell
   - Enter the **Selling Price** per unit
   - Click **"➕ Add to Cart"**

3. **Add Multiple Items** (Optional)
   - Repeat step 2 for each product
   - All items will appear in the shopping cart
   - Cart total updates automatically

4. **Set Customer Information** (Optional)
   - Enter customer name (defaults to "Walk-in Customer")

5. **Generate the Receipt**
   - Review items in the cart
   - Click **"🧾 Generate Receipt"**
   - The receipt will be generated and displayed
   - Inventory is automatically updated

6. **Save or Print the Receipt**
   - Click **"💾 Save Receipt"** to save as a text file
   - Receipt window shows all details
   - Close the window when done

### Viewing Past Receipts

1. Scroll down to the **"Recent Receipts"** section
2. All generated receipts are listed with:
   - Invoice Number
   - Customer Name
   - Total Amount
   - Date & Time
3. **Double-click** any receipt to view details
4. **Right-click** for options:
   - View Receipt
   - Delete Receipt

### Managing the Cart

- **Remove Items**: Right-click on any item in the cart and select "Remove Item"
- **Clear Cart**: Click "🗑️ Clear Cart" to remove all items
- Cart shows running total at the bottom

## Database Structure

The receipt system uses three main tables:

### 1. `receipts` table
Stores receipt metadata:
- `invoice_number` (PRIMARY KEY)
- `customer_name`
- `total_amount`
- `tax_amount`
- `grand_total`
- `purchase_date`

### 2. `receipt_items` table
Stores individual items in each receipt:
- `id` (PRIMARY KEY)
- `invoice_number` (FOREIGN KEY)
- `product_id`
- `product_name`
- `quantity`
- `price_per_unit`
- `total_price`

### 3. `purchases` table (Updated)
Enhanced to track sales with invoice numbers:
- `id` (PRIMARY KEY)
- `invoice_number` (UNIQUE)
- `product_name`
- `quantity`
- `selling_price_per_unit`
- `stock_price_per_unit`
- `total_selling_price`
- `total_stock_cost`
- `profit`
- `purchase_date`

## Architecture

The receipt system follows a modular architecture:

```
app/
├── receipt_repository.py      # Database operations
├── receipt_generator.py       # Receipt formatting and display
├── receipt_ui_components.py   # User interface components
├── receipt_manager.py         # Main coordinator
└── db.py                      # Database schema (updated)
```

### Components

1. **ReceiptRepository** (`receipt_repository.py`)
   - Handles all database operations
   - Creates receipts and items
   - Manages inventory updates
   - Validates stock availability

2. **ReceiptGenerator** (`receipt_generator.py`)
   - Formats receipts in professional text format
   - Creates receipt windows
   - Handles saving and printing

3. **ReceiptUIComponents** (`receipt_ui_components.py`)
   - Creates all UI elements
   - Input forms, cart view, receipt list
   - Context menus and interactions

4. **ReceiptManager** (`receipt_manager.py`)
   - Coordinates all operations
   - Manages cart state
   - Handles user actions

## Customization

### Company Information

Edit `app/receipt_generator.py` to customize company details:

```python
class ReceiptGenerator:
    def __init__(self):
        self.company_name = "Your Company Name"
        self.company_address = "Your Address"
        self.company_city = "City, State ZIP"
        self.company_phone = "Tel: (XXX) XXX-XXXX"
        self.company_email = "Email: your@email.com"
```

### Tax Configuration

To add tax to receipts, modify the tax_rate in `receipt_manager.py`:

```python
invoice_number = self.repo.create_receipt(
    items=self.cart_items,
    customer_name=customer_name,
    tax_rate=0.08  # 8% tax
)
```

### Receipt Format

Customize the receipt format in `receipt_generator.py`:
- Modify `generate_receipt_text()` method
- Adjust column widths, spacing, or styling
- Add additional fields or sections

## Key Features Explained

### 1. Invoice Number Generation
- Format: `INV-YYYYMMDD-XXXX`
- YYYYMMDD: Current date
- XXXX: Random 4-digit number
- Guaranteed unique across all receipts

### 2. Stock Validation
- Checks available stock before adding to cart
- Prevents overselling
- Shows real-time stock availability
- Updates stock atomically (all-or-nothing)

### 3. Profit Tracking
- Calculates profit per item: (Selling Price - Stock Price) × Quantity
- Stores in purchases table
- Available for reports and analytics

### 4. Transaction Safety
- Uses database transactions
- Rolls back on errors
- Ensures data consistency
- Restores stock on deletion

## Troubleshooting

### Common Issues

1. **"Product with ID X not found"**
   - Ensure the product exists in inventory
   - Check the product ID is correct

2. **"Insufficient stock for [Product]"**
   - Not enough items in inventory
   - Reduce quantity or restock first

3. **Receipt window doesn't open**
   - Check for error messages
   - Ensure all items are valid

4. **Cart items not appearing**
   - Verify you clicked "Add to Cart"
   - Check quantity and price are valid

### Error Recovery

If something goes wrong:
- Cart items are preserved until cleared
- Database transactions prevent partial updates
- Deleting a receipt restores stock
- No data loss on errors

## Tips and Best Practices

1. **Always verify stock** before adding large quantities
2. **Use descriptive customer names** for easier tracking
3. **Save receipts** to customer files for records
4. **Review cart** before generating receipt
5. **Regular backups** of the database file

## Future Enhancements

Possible improvements:
- PDF receipt generation
- Email receipts to customers
- Receipt templates
- Payment method tracking
- Discount/coupon support
- Barcode scanning
- Receipt search functionality
- Sales reports and analytics

## Support

For issues or questions:
- Check this guide first
- Review error messages carefully
- Ensure database is not corrupted
- Verify Python dependencies are installed

## Version

- **Version**: 1.0
- **Date**: November 2024
- **Compatible with**: Inventory Management System v1.x

---

**Note**: This receipt generation system is fully integrated with your existing inventory management system. All sales automatically update inventory levels and are tracked for profit calculations.

