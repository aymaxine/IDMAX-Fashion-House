import sqlite3
import os

# Get the absolute path to the database file
db_path = os.path.abspath(os.path.join('instance', 'fashion_catalog.db'))

try:
    # Connect to the SQLite database
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the column exists
    cursor.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"Current columns in products table: {columns}")
    
    if 'active' not in columns:
        # Add the active column to the products table
        print("Adding 'active' column to the products table...")
        cursor.execute("ALTER TABLE products ADD COLUMN active BOOLEAN DEFAULT 1 NOT NULL")
        conn.commit()
        print("Successfully added 'active' column to products table")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(products)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns in products table: {updated_columns}")
    else:
        print("Column 'active' already exists in products table")
        
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    # Close the connection
    if 'conn' in locals():
        conn.close()
        print("Database connection closed")
