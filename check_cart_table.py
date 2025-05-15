"""
Check if the cart_items table exists in the database
"""
from app import create_app, db
from app.models.cart import CartItem
from sqlalchemy import inspect

# Create Flask app with development configuration
app = create_app()

# Create application context
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("Available tables in the database:")
    for table in tables:
        print(f"- {table}")
    
    if 'cart_items' in tables:
        print("\nCart items table exists!")
        
        # Check columns in cart_items table
        columns = inspector.get_columns('cart_items')
        print("\nColumns in cart_items table:")
        for column in columns:
            print(f"- {column['name']}: {column['type']}")
    else:
        print("\nCart items table does NOT exist!")
