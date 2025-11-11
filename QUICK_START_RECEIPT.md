# Quick Start: Receipt Generation System

## 5-Minute Guide to Creating Your First Receipt

### Step 1: Add Products to Inventory
Before you can create receipts, you need products in your inventory.

1. Go to **📦 Inventory** tab
2. Add some products:
   - Product Name: "apple"
   - Quantity: 100
   - Price per kg: 2.50
   - Category: "fruits"
3. Note the Product ID (shown in the first column)

### Step 2: Open Receipt Generation
1. Click on the **🧾 Receipt Generation** tab
2. You'll see a form to add products to cart

### Step 3: Create a Receipt

#### Simple Single-Item Receipt

1. **Enter Product ID**: Type `1` (or your product's ID)
2. **Click "🔍 Fetch Details"**: 
   - Product name will appear
   - Available stock will show
   - Price will auto-fill
3. **Enter Quantity**: Type `5`
4. **Enter Selling Price**: Type `3.00` (sell for $3 per unit)
5. **Click "➕ Add to Cart"**
6. **Click "🧾 Generate Receipt"**

Done! Your receipt is generated and displayed.

#### Multi-Item Receipt

1. Add first item (follow steps above)
2. Add second item:
   - Product ID: `2`
   - Fetch Details
   - Quantity: `10`
   - Selling Price: `4.50`
   - Add to Cart
3. Add third item (repeat as needed)
4. Review cart - shows all items and total
5. Click "🧾 Generate Receipt"

### Step 4: Save the Receipt
1. In the receipt window, click **"💾 Save Receipt"**
2. Choose location and filename
3. Receipt saved as text file

## Receipt Example

```
============================================================
         Inventory Management Store
            123 Business Street
            City, State 12345
         Tel: (123) 456-7890
      Email: info@inventorystore.com
============================================================

INVOICE NUMBER: INV-20241111-1234
DATE: 2024-11-11 14:30:15
CUSTOMER: Walk-in Customer
------------------------------------------------------------

ITEM                          QTY      PRICE        TOTAL
------------------------------------------------------------
Apple                           5      $3.00       $15.00
Banana                         10      $4.50       $45.00
------------------------------------------------------------
SUBTOTAL:                                         $60.00
============================================================
GRAND TOTAL:                                      $60.00
============================================================

           Thank you for your business!
              Please come again!
============================================================
```

## Key Features

### 🎯 Quick Tips
- **Product ID**: Get from inventory list (first column)
- **Selling Price**: Can be different from stock price (markup)
- **Customer Name**: Optional, defaults to "Walk-in Customer"
- **Cart**: Review before generating receipt
- **Stock Check**: System prevents overselling

### 📋 What Happens When You Generate a Receipt?
1. ✅ Unique invoice number created
2. ✅ All items recorded in database
3. ✅ Inventory quantities updated automatically
4. ✅ Profit calculated and tracked
5. ✅ Receipt displayed and ready to save/print

### 🔄 Managing Receipts
- **View Past Receipts**: Scroll to "Recent Receipts" section
- **Reprint**: Double-click any receipt
- **Delete**: Right-click → Delete (restores stock)
- **Search**: Find by invoice number or customer

### ⚠️ Common Mistakes to Avoid
- ❌ Forgetting to fetch product details first
- ❌ Entering quantity more than available stock
- ❌ Not reviewing cart before generating
- ❌ Leaving fields empty

### ✅ Best Practices
- ✅ Always fetch details before adding to cart
- ✅ Double-check quantities and prices
- ✅ Add customer name for easier tracking
- ✅ Save receipts to file for records
- ✅ Review cart total before generating

## Workflow Diagram

```
1. Enter Product ID
         ↓
2. Fetch Product Details
         ↓
3. Enter Quantity & Price
         ↓
4. Add to Cart ←──────┐
         ↓             │
5. Add More Items? ───┘ (Yes)
         ↓ (No)
6. Review Cart
         ↓
7. Generate Receipt
         ↓
8. Save/Print Receipt
         ↓
9. Done! ✓
```

## Try These Examples

### Example 1: Small Purchase
- 1 item, quantity 2, price $5.00
- Customer: "John Doe"
- Total: $10.00

### Example 2: Bulk Order
- 3 different items
- Total quantities: 50+ units
- Customer: "ABC Restaurant"
- Total: $200+

### Example 3: Quick Sale
- 1 item, quantity 1
- Use default customer name
- Quick checkout

## Need Help?

### Stock Not Available?
Go to Inventory tab and add stock first.

### Wrong Product ID?
Check the inventory list for correct IDs.

### Can't Save Receipt?
Make sure you have write permissions in the selected folder.

### Receipt Not Generating?
- Check all fields are filled
- Verify stock is available
- Look for error messages

## Next Steps

1. ✅ Create your first receipt
2. ✅ Try a multi-item receipt
3. ✅ View past receipts
4. ✅ Customize company information (see main guide)
5. ✅ Explore the purchase tracking features

---

**You're ready to go!** Start by adding some inventory, then create your first receipt. It's that simple! 🎉

