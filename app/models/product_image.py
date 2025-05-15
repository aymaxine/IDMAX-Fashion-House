from app import db
from datetime import datetime

class ProductImage(db.Model):
    """
    Model for product images
    """
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationship with Product
    product = db.relationship('Product', backref=db.backref('images', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return 'ProductImage({}, {})'.format(self.product_id, self.filename)
