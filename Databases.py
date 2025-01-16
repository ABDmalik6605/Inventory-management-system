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
