from app import create_app, db
from app.models.models import Product
import sqlalchemy as sa

def check_product_structure():
    """Check the structure of the products table"""
    app = create_app()
    with app.app_context():
        # Print the columns of the products table
        columns = [column.name for column in Product.__table__.columns]
        print(f"Columns in Product model: {columns}")
        
        # Check if 'active' column exists in the database
        inspector = sa.inspect(db.engine)
        db_columns = [column['name'] for column in inspector.get_columns('products')]
        print(f"Columns in database: {db_columns}")
        
        if 'active' not in db_columns:
            print("The 'active' column does not exist in the database yet.")
        else:
            print("The 'active' column exists in the database.")

if __name__ == "__main__":
    check_product_structure()
