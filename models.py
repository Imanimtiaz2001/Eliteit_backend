from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    name = db.Column(db.String(255))  # Name of the user
    city = db.Column(db.String(100))  # User's city
    state = db.Column(db.String(100))  # User's state
    pin_code = db.Column(db.String(20))  # User's pin code
    logo = db.Column(db.String(255))  # User's logo (URL or file path)
    gst_number = db.Column(db.String(50))  # GST number (optional)
    profile_photo = db.Column(db.String(255))  # New field for storing profile photo (URL or file path)


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
