from app import db
from datetime import datetime

class ActivityLog(db.Model):
    """
    Model for tracking admin activities in the system
    """
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    entity_type = db.Column(db.String(50), nullable=True)  # 'product', 'brand', 'user', etc.
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User model
    user = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.user.username}>'
