from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db
from run import app

# Create the Flask-Script manager
manager = Manager(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Add migration commands to manager
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
