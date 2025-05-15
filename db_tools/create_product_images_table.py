"""
Create the product_images table in the database if it doesn't exist
"""
import os
import sys
from flask import Flask
import sqlite3
from datetime import datetime

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a minimal Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/fashion_catalog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def create_product_images_table():
    """Create the product_images table if it doesn't exist"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'fashion_catalog.db')
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if product_images table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_images'")
    if cursor.fetchone() is None:
        print("Creating product_images table...")
        
        # Create the table
        cursor.execute('''
        CREATE TABLE product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            is_primary BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
        ''')
        
        print("Table created successfully!")
    else:
        print("product_images table already exists.")
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_product_images_table()
    print("Done!")
