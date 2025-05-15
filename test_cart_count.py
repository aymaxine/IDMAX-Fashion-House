"""
Test the User.get_cart_count method
"""
from app import create_app, db
from app.models.models import User
from app.models.cart import CartItem
from sqlalchemy import func

# Create Flask app with development configuration
app = create_app()

# Create application context
with app.app_context():
    # Get a user
    user = User.query.first()
    
    if not user:
        print("No users found in the database.")
        exit(1)
    
    print(f"Testing get_cart_count for user: {user.username}")
    
    # Test original method
    try:
        # Original method
        from app.models.cart import CartItem
        result = CartItem.query.filter_by(user_id=user.id).with_entities(db.func.sum(CartItem.quantity)).scalar() or 0
        print(f"Original method result: {result}")
    except Exception as e:
        print(f"Error with original method: {str(e)}")
    
    # Test modified method
    try:
        # Modified method
        from sqlalchemy import func
        result = db.session.query(func.coalesce(func.sum(CartItem.quantity), 0))\
            .filter(CartItem.user_id == user.id).scalar()
        print(f"Modified method result: {result}")
    except Exception as e:
        print(f"Error with modified method: {str(e)}")
        
    # Test even simpler method
    try:
        # Simplest approach
        cart_items = CartItem.query.filter_by(user_id=user.id).all()
        count = sum(item.quantity for item in cart_items)
        print(f"Simple iteration result: {count}")
    except Exception as e:
        print(f"Error with simple iteration: {str(e)}")
        
    # Check if cart_items table has any data
    try:
        total_items = CartItem.query.count()
        print(f"Total CartItem records in database: {total_items}")
        
        if total_items > 0:
            print("\nSample cart items:")
            items = CartItem.query.limit(5).all()
            for item in items:
                print(f"- User: {item.user_id}, Product: {item.product_id}, Quantity: {item.quantity}")
    except Exception as e:
        print(f"Error checking cart_items data: {str(e)}")
