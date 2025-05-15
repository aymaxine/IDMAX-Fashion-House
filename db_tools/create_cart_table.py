"""
Create the cart_items table in the database
"""
from app import create_app, db
from app.models.cart import CartItem

# Create Flask app with development configuration
app = create_app()

# Create application context
with app.app_context():
    print("Creating cart_items table...")
    # Create only the cart_items table
    CartItem.__table__.create(db.engine, checkfirst=True)
    print("Cart items table created successfully!")
