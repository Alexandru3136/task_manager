from flask import Flask
from app import db  # Importă instanța globală

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # Inițializează baza de date cu aplicația

    with app.app_context():
        db.create_all()  # Creează tabelele

    return app
