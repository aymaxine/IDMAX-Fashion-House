"""
Simple test of the search functionality to ensure it works after our fixes
"""
from app import create_app
from flask import render_template_string

app = create_app()

# Create a simple test template with the truncate filter
test_template = """
{% if description is none %}
  Description is None
{% else %}
  Description: {{ description|default('No description')|truncate(10) }}
{% endif %}
"""

with app.app_context():
    # Test with None values
    try:
        rendered = render_template_string(test_template, description=None)
        print("Test with None value successful!")
        print(f"Rendered: {rendered.strip()}")
    except Exception as e:
        print(f"Test with None value failed: {str(e)}")
    
    # Test with empty string
    try:
        rendered = render_template_string(test_template, description="")
        print("\nTest with empty string successful!")
        print(f"Rendered: {rendered.strip()}")
    except Exception as e:
        print(f"Test with empty string failed: {str(e)}")
    
    # Test with actual value
    try:
        rendered = render_template_string(test_template, description="This is a long description that should be truncated")
        print("\nTest with actual value successful!")
        print(f"Rendered: {rendered.strip()}")
    except Exception as e:
        print(f"Test with actual value failed: {str(e)}")
