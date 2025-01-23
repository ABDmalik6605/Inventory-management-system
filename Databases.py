import sqlite3

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
            load1 INTEGER DEFAULT 0,
            load2 INTEGER DEFAULT 0,
            totalload INTEGER DEFAULT 0,
            return INTEGER DEFAULT 0,
            payment REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# Add a new product to the inventory and sync with the salesman table
def add_product_to_inventory(name, quantity, price_per_kg, total_price, category):
    conn_inventory = sqlite3.connect("inventory.db")
    cursor_inventory = conn_inventory.cursor()

    # Insert the product into the inventory
    cursor_inventory.execute("""
        INSERT INTO inventory (name, quantity, price_per_kg, total_price, category)
        VALUES (?, ?, ?, ?, ?)
    """, (name, quantity, price_per_kg, total_price, category))
    conn_inventory.commit()
    conn_inventory.close()

    # Sync with the salesman database
    sync_product_with_salesman(name)

# Sync inventory product with the salesman table
def sync_product_with_salesman(product_name):
    conn_salesman = sqlite3.connect("salesman.db")
    cursor_salesman = conn_salesman.cursor()

    # Get all salesmen
    cursor_salesman.execute("SELECT id, name FROM salesman")
    salesmen = cursor_salesman.fetchall()

    for salesman_id, salesman_name in salesmen:
        # Check if the product already exists for this salesman
        cursor_salesman.execute("""
            SELECT COUNT(*) FROM salesman
            WHERE name = ? AND product = ?
        """, (salesman_name, product_name))
        exists = cursor_salesman.fetchone()[0]

        if not exists:
            # Insert the product with default values
            cursor_salesman.execute("""
                INSERT INTO salesman (name, product, load1, load2, totalload, return, payment)
                VALUES (?, ?, 0, 0, 0, 0, 0)
            """, (salesman_name, product_name))

    conn_salesman.commit()
    conn_salesman.close()

# Add a new salesman
def add_salesman(name):
    conn_salesman = sqlite3.connect("salesman.db")
    cursor_salesman = conn_salesman.cursor()

    # Insert a new salesman
    cursor_salesman.execute("INSERT INTO salesman (name, product) VALUES (?, '')", (name,))
    conn_salesman.commit()
    conn_salesman.close()

    # Sync existing inventory products with the new salesman
    sync_inventory_with_salesman(name)

# Sync all inventory products with a new salesman
def sync_inventory_with_salesman(salesman_name):
    conn_inventory = sqlite3.connect("inventory.db")
    cursor_inventory = conn_inventory.cursor()

    # Get all products from the inventory
    cursor_inventory.execute("SELECT name FROM inventory")
    products = cursor_inventory.fetchall()
    conn_inventory.close()

    conn_salesman = sqlite3.connect("salesman.db")
    cursor_salesman = conn_salesman.cursor()

    for product_name, in products:
        # Add the product to the new salesman's record with default values
        cursor_salesman.execute("""
            INSERT INTO salesman (name, product, load1, load2, totalload, return, payment)
            VALUES (?, ?, 0, 0, 0, 0, 0)
        """, (salesman_name, product_name))

    conn_salesman.commit()
    conn_salesman.close()
