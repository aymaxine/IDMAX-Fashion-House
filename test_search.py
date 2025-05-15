"""
Test the search functionality
"""
from app import create_app
from flask import url_for

# Create Flask app with test configuration
app = create_app()

def test_search_route():
    """Test that the search route works and returns correct results"""
    with app.test_client() as client:
        # Test empty search
        response = client.get('/search')
        assert response.status_code == 200
        assert b'No search query provided' in response.data
        
        # Test search with query
        response = client.get('/search?query=shirt')
        assert response.status_code == 200
        
        # Test search with non-existent query
        response = client.get('/search?query=xyznonexistentthing')
        assert response.status_code == 200
        assert b'No results found' in response.data

if __name__ == '__main__':
    with app.app_context():
        print("Testing search functionality...")
        try:
            test_search_route()
            print("✅ Search route tests passed!")
        except AssertionError as e:
            print(f"❌ Search test failed: {str(e)}")
            
        # Display all available routes
        print("\nRegistered routes:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")
