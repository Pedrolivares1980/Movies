from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    Represents a user with authentication and authorization information.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_image = db.Column(db.String, nullable=True)  # URL of the profile image
    movies = db.relationship('Movie', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Movie(db.Model):
    """
    Represents a movie with its details and related reviews.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String, nullable=True)  # URL of the movie cover image
    director = db.Column(db.String(100), nullable=False)
    trailer_link = db.Column(db.String, nullable=False)  # Ensuring this field is not empty
    cast = db.Column(db.String(500), nullable=True)  # Nullable if not every movie has a cast listed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviews = db.relationship('Review', backref='movie', lazy='dynamic', cascade="all, delete-orphan")

class Review(db.Model):
    """
    Represents a review by a user for a movie.
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=func.now())
    date_updated = db.Column(db.DateTime, nullable=False, default=func.now(), onupdate=func.now())
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
