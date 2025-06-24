from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SECRET_KEY'] = 'superclave-secreta-angel-2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dataflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/uploads'

    db.init_app(app)

    # Registro de blueprints y modelos
    from .routes import main
    app.register_blueprint(main)

    return app
