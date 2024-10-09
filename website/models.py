from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
#from flask_sqlalchemy import SQLAlchemy

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    is_admin = db.Column(db.Boolean, default=False)  # Add this field

    # Relationship to link users to their predictions
    # predictions = db.relationship('PredictionReport', backref='user', lazy=True)


class PredictionReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)  # Foreign key to link to the User model
    filename = db.Column(db.String(100), nullable=False)  # File name of the uploaded image
    prediction = db.Column(db.String(50), nullable=False)  # Predicted result
    date = db.Column(db.DateTime, default=func.now())  # Timestamp of the prediction
