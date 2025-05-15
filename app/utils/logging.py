from app import db
from app.models.activity_log import ActivityLog
from flask_login import current_user

def log_activity(action, entity_type=None, entity_id=None, details=None):
    """
    Log an admin activity
    
    Args:
        action (str): Description of the action performed
        entity_type (str, optional): Type of entity affected (product, brand, user)
        entity_id (int, optional): ID of the entity affected
        details (str, optional): Additional details about the action
    """
    if not current_user or not current_user.is_authenticated:
        return
        
    log = ActivityLog(
        user_id=current_user.id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.session.add(log)
    db.session.commit()
