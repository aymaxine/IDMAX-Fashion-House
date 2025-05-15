from app import create_app, db
import sqlalchemy as sa
import traceback
import sys

def add_active_field():
    """Add 'active' field to products table"""
    
    try:
        app = create_app()
        with app.app_context():
            try:
                # Check if column exists
                inspector = sa.inspect(db.engine)
                columns = [column['name'] for column in inspector.get_columns('products')]
                print(f"Current columns in products table: {columns}")
                
                if 'active' not in columns:
                    # Add the active column to the products table
                    print("Adding 'active' column to the products table...")
                    conn = db.engine.connect()
                    trans = conn.begin()
                    try:
                        conn.execute(sa.text("ALTER TABLE products ADD COLUMN active BOOLEAN DEFAULT 1 NOT NULL"))
                        trans.commit()
                        print("Successfully added 'active' column to products table")
                    except Exception as e:
                        trans.rollback()
                        print(f"Failed to add column: {str(e)}")
                        print(traceback.format_exc())
                    finally:
                        conn.close()
                else:
                    print("Column 'active' already exists in products table")
                
                # Verify the change
                inspector = sa.inspect(db.engine)
                columns = [column['name'] for column in inspector.get_columns('products')]
                print(f"Updated columns in products table: {columns}")
                
            except Exception as e:
                print(f"Database inspection error: {str(e)}")
                print(traceback.format_exc())
                
                # Check if the Product model already has the active column
                from app.models.models import Product
                if hasattr(Product, 'active'):
                    print("The 'active' column exists in the model but there was an error checking the database")
                else:
                    print("The 'active' column is not defined in the model")
    except Exception as e:
        print(f"Application setup error: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    print("Starting to add active field to products table...")
    add_active_field()
    print("Script completed.")
