import os
import tempfile
import pytest
from app import create_app, db
from app.models.models import Brand, Product

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
    })
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        
        # Add test data
        add_sample_data()
    
    yield app
    
    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


def add_sample_data():
    """Add sample data to the database for testing."""
    # Add brands
    brand1 = Brand(name='Test Brand 1')
    brand2 = Brand(name='Test Brand 2')
    db.session.add_all([brand1, brand2])
    db.session.commit()
    
    # Add products
    product1 = Product(
        product_id='TEST001',
        name='Test Product 1',
        brand_id=brand1.id,
        gender='Unisex',
        price=999.99,
        num_images=3,
        description='This is a test product',
        primary_color='Blue'
    )
    
    product2 = Product(
        product_id='TEST002',
        name='Test Product 2',
        brand_id=brand2.id,
        gender='Men',
        price=499.99,
        num_images=2,
        description='This is another test product',
        primary_color='Red'
    )
    
    product3 = Product(
        product_id='TEST003',
        name='Test Product 3',
        brand_id=brand1.id,
        gender='Women',
        price=1299.99,
        num_images=5,
        description='This is a third test product',
        primary_color='Green'
    )
    
    db.session.add_all([product1, product2, product3])
    db.session.commit()
