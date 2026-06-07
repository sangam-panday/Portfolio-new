from flask import Flask
import os
from dotenv import load_dotenv
load_dotenv()

from .extension import (
    db,
    login_manager,
    mail
)

from .auth.routes import auth_bp
from .main.routes import main_bp
from .models import User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True

    app.config['MAIL_USERNAME'] = os.getenv(
        'EMAIL_USER'
    )

    app.config['MAIL_PASSWORD'] = os.getenv(
        'EMAIL_PASSWORD'
    )

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app