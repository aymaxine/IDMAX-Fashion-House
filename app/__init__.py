import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
bcrypt = Bcrypt()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    if test_config is None:
        # Load the instance config, if it exists
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///fashion_catalog.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)    # Register blueprints
    from app.routes import main_bp, products_bp, brands_bp, auth_bp, admin_bp, admin_orders_bp, static_pages_bp, api_bp, export_bp, cart_bp, orders_bp
    from app.routes.compare import compare_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_orders_bp)
    app.register_blueprint(static_pages_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(compare_bp)
    app.register_blueprint(orders_bp)
    
    # Register error handlers
    from app.handlers import register_error_handlers
    register_error_handlers(app)
    
    # Add context processor for current year
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}

    return app
