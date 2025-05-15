from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """
    User model for authentication
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_cart_count(self):
        """
        Returns the total number of items in the user's cart
        """
        from app.models.cart import CartItem
        
        # Simple iteration approach - more reliable
        cart_items = CartItem.query.filter_by(user_id=self.id).all()
        return sum(item.quantity for item in cart_items)
        
    def __repr__(self):
        return f'<User {self.username}>'

class Brand(db.Model):
    """
    Brand model representing the different product brands
    """
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    products = db.relationship('Product', backref='brand_info', lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Brand {self.name}>'


class Product(db.Model):
    """
    Product model representing fashion products
    """
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)    
    gender = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    num_images = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    primary_color = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'
