from flask import Flask

from .extension import (
    db,
    login_manager
)

from .auth.routes import auth_bp
from .main.routes import main_bp
from .models import User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
    

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app