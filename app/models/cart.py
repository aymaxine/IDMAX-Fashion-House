from app import db
from datetime import datetime

class CartItem(db.Model):
    """
    Model for cart items
    """
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define relationships
    user = db.relationship('User', backref=db.backref('cart_items', lazy='dynamic', cascade='all, delete-orphan'))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy='dynamic'))

    def __repr__(self):
        return f'CartItem(user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})'
