from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect  # Add this line
from config import Config
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()  # Add this line
mail = Mail()

login_manager.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)  # Add this line
    mail.init_app(app)

    # Set custom AnonymousUser
    from app.models import AnonymousUser
    login_manager.anonymous_user = AnonymousUser

    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()  # Create tables if they don't exist

    return app
