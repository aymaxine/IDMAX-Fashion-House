import pytest
from app.models.models import Brand, Product

def test_brand_model(app):
    """Test the Brand model."""
    with app.app_context():
        brand = Brand.query.filter_by(name='Test Brand 1').first()
        
        assert brand is not None
        assert brand.name == 'Test Brand 1'
        
        # Test relationship with products
        assert brand.products.count() == 2
        
        # Test string representation
        assert str(brand) == '<Brand Test Brand 1>'


def test_product_model(app):
    """Test the Product model."""
    with app.app_context():
        product = Product.query.filter_by(product_id='TEST001').first()
        
        assert product is not None
        assert product.name == 'Test Product 1'
        assert product.gender == 'Unisex'
        assert product.price == 999.99
        assert product.primary_color == 'Blue'
        
        # Test relationship with brand
        assert product.brand_info.name == 'Test Brand 1'
        
        # Test string representation
        assert str(product) == '<Product Test Product 1>'


def test_brand_product_relationship(app):
    """Test the relationship between Brand and Product models."""
    with app.app_context():
        brand = Brand.query.filter_by(name='Test Brand 1').first()
        products = brand.products.all()
        
        assert len(products) == 2
        assert products[0].name == 'Test Product 1'
        assert products[1].name == 'Test Product 3'
        
        # Test cascade delete
        db_product_count = Product.query.count()
        assert db_product_count == 3
        
        brand_id = brand.id
        Product.query.filter_by(brand_id=brand_id).delete()
        
        db_product_count_after = Product.query.count()
        assert db_product_count_after == 1  # Only one product left from brand 2
