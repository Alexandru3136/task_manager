from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'user_bp.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import blueprint-urile AICI, după inițializarea `app`
    from .routes.task_routes import task_bp
    from .routes.user_routes import user_bp

    with app.app_context():
        # Importuri întârziate pentru User și Task
        from app.models.user import User
        from app.models.task import Task
        from .routes import task_routes, user_routes
        app.register_blueprint(task_routes.task_bp)
        app.register_blueprint(user_routes.user_bp)

        # Creează toate tabelele în baza de date
        db.create_all()

    # Ruta principală
    @app.route('/')
    def home():
        return redirect(url_for('user_bp.login'))  # Redirecționează mereu la login la pornirea aplicației

    return app
