import pytest

def test_index_page(client):
    """Test the index page returns 200 status code."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Fashion Product Catalog' in response.data


def test_product_detail_page(client):
    """Test the product detail page."""
    response = client.get('/products/TEST001')
    assert response.status_code == 200
    assert b'Test Product 1' in response.data
    assert b'999.99' in response.data
    assert b'Unisex' in response.data


def test_brand_list_page(client):
    """Test the brand list page."""
    response = client.get('/brands/')
    assert response.status_code == 200
    assert b'Test Brand 1' in response.data
    assert b'Test Brand 2' in response.data


def test_brand_detail_page(client):
    """Test the brand detail page."""
    # Get the first brand from the database
    response = client.get('/brands/1')
    assert response.status_code == 200
    assert b'Test Brand 1' in response.data
    assert b'Test Product 1' in response.data


def test_nonexistent_product(client):
    """Test accessing a nonexistent product returns 404."""
    response = client.get('/products/NONEXISTENT')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data


def test_nonexistent_brand(client):
    """Test accessing a nonexistent brand returns 404."""
    response = client.get('/brands/999')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data


def test_product_filtering(client):
    """Test product filtering on the index page."""
    # Filter by gender
    response = client.get('/?gender=Men')
    assert response.status_code == 200
    assert b'Test Product 2' in response.data
    assert b'Test Product 1' not in response.data
    assert b'Test Product 3' not in response.data
    
    # Filter by brand
    response = client.get('/?brand_id=1')
    assert response.status_code == 200
    assert b'Test Product 1' in response.data
    assert b'Test Product 3' in response.data
    assert b'Test Product 2' not in response.data
    
    # Filter by color
    response = client.get('/?color=Red')
    assert response.status_code == 200
    assert b'Test Product 2' in response.data
    assert b'Test Product 1' not in response.data
    assert b'Test Product 3' not in response.data
