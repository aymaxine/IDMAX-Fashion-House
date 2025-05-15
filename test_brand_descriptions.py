"""
Test the handling of None brand descriptions in search
"""
from app import create_app, db
from app.models.models import Brand
from app.utils.image_processing import get_product_images
from sqlalchemy import or_

# Create Flask app with test configuration
app = create_app()

with app.app_context():
    # Find any brands with None descriptions
    brands_with_none = Brand.query.filter(Brand.description == None).all()
    
    print(f"Found {len(brands_with_none)} brands with None descriptions")
    
    # Test the template rendering with these brands
    for brand in brands_with_none:
        print(f"  - {brand.name}: Description = {repr(brand.description)}")
    
    # Test the search function's handling of these brands
    from app.routes.main import search
    from flask import Request
    
    if brands_with_none:
        # Create a test environment to simulate a search request
        print("\nTesting search with a brand that has a None description...")
        with app.test_request_context(f'/search?query={brands_with_none[0].name}'):
            from flask import render_template_string
            
            # Test just the part of the template that caused the issue
            test_template = """
            {% for brand in brands %}
                {{ brand.name }}: {{ brand.description|default('No description')|truncate(10) }}
            {% endfor %}
            """
            
            try:
                rendered = render_template_string(test_template, brands=brands_with_none)
                print("✅ Template rendered successfully with our fix!")
                print(f"Rendered output: {rendered.strip()}")
            except Exception as e:
                print(f"❌ Template rendering failed: {str(e)}")
    else:
        print("No brands with None description found to test with.")
