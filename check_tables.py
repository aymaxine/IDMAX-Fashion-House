import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/fashion_catalog.db')
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(f"- {table[0]}")

# Check if cart_items exists
if ('cart_items',) in tables:
    print("\nCart items table exists!")
    
    # Get columns in cart_items table
    cursor.execute("PRAGMA table_info(cart_items)")
    columns = cursor.fetchall()
    
    print("\nColumns in cart_items table:")
    for column in columns:
        print(f"- {column[1]}: {column[2]}")
else:
    print("\nCart items table does NOT exist!")

# Close connection
conn.close()
