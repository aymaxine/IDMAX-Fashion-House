import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the database instance and application factory
from app import db, create_app
from app.models.order import Order, OrderItem

def create_orders_tables():
    """Create orders and order_items tables"""
    app = create_app()
    
    with app.app_context():
        # Check if tables already exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'orders' not in existing_tables or 'order_items' not in existing_tables:
            print("Creating orders tables...")
            # Create tables
            db.create_all()  # This will create all tables not yet in the database
            print("Orders tables created successfully.")
        else:
            print("Orders tables already exist.")

if __name__ == '__main__':
    create_orders_tables()
