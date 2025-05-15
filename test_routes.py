"""
Test if the checkout route works correctly
"""
from app import create_app

# Create Flask app with development configuration
app = create_app()

# Print out all registered routes
with app.app_context():
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")

    # Check specifically for cart routes
    print("\nCart routes:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith('cart.'):
            print(f"{rule.endpoint}: {rule}")
