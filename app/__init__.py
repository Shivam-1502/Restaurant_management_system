from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate  # Import Flask-Migrate
from app.models import db, Admin, Employee

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant_management.db'  # Change this if using MySQL

    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Define user_loader function
    @login_manager.user_loader
    def load_user(user_id):
        role, user_id = user_id.split("-")
        user_id = int(user_id)
        
        if role == "admin":
            return Admin.query.get(user_id)
        elif role == "employee":
            return Employee.query.get(user_id)
        return None  # User not found

    # Import and register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.employee_routes import employee_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(employee_bp, url_prefix='/employee')

    return app
