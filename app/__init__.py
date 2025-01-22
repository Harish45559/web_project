from flask import Flask  # Ensure Flask is imported
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()


bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    with app.app_context():
        # Import and register the Blueprint
        from .routes import main
        app.register_blueprint(main)

        return app
