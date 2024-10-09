from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import tensorflow as tf
from tensorflow.keras.models import load_model  # Import Keras load_model directly

print(tf.__version__)

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Load the Keras model (.h5 or .keras)
    model_path = path.join(path.dirname(__file__),'model.h5')  # Adjust the path if needed
    print(f"Loading model from: {model_path}")

    if path.exists(model_path) and model_path.endswith(('.h5')):
        try:
            # Load the model as a Keras model
            app.model = load_model(model_path)
            app.class_names = ['normal', 'tumor']
            print("Model loaded successfully!")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    else:
        raise FileNotFoundError(f"Model file not found or incorrect format at {model_path}")
    
    

    return app

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Created database!")
