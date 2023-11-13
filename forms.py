from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional
from flask_wtf.file import FileAllowed

class ReviewForm(FlaskForm):
    content = TextAreaField('Review', validators=[DataRequired(message="Please enter your review content.")])
    submit = SubmitField('Submit Review')

class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    genre = SelectField('Genre', choices=[
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('fantasy', 'Fantasy'),
        ('horror', 'Horror'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('thriller', 'Thriller'),
        ('adventure', 'Adventure'),
        ('family', 'Family'),
        ('animation', 'Animation')
    ])
    director = StringField('Director', validators=[DataRequired()])
    overview = TextAreaField('Overview', validators=[DataRequired()])
    cast = TextAreaField('Cast', description="List the main cast. Separate names with commas.")
    cover_image = FileField('Cover Image' , validators=[
        FileAllowed(['jpg', 'jpeg' 'png', 'webp'], 'Only JPG, JPEG, PNG and WEBP images are allowed.')
    ])
    trailer_link = StringField('Trailer Link', validators=[
        DataRequired(message="Please provide a link to the movie trailer."),
        Regexp(regex=r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$',
               message="Please enter a valid URL.")])
    submit = SubmitField('Add Movie')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Please enter a username."),
        Length(min=4, max=25, message="Username must be between 4 and 25 characters."),
        Regexp(regex=r'^[\w.@+-]+$', message="Username has invalid characters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Please enter your email address."),
        Email(message="Invalid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter a password."),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message='Passwords must match.')
    ])
    profile_image = FileField('Profile Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'webp'], 'Only JPG, WEBP and PNG images are allowed.')
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired(message="Please enter your username or email.")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter your password.")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    """
    FlaskForm for user profile updates.
    Includes fields for username, email, and profile image.
    """
    username = StringField('Username', validators=[
        DataRequired(message="Please enter a username."),
        Length(min=4, max=25, message="Username must be between 4 and 25 characters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Please enter your email address."),
        Email(message="Please enter a valid email address.")
    ])
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed.')
    ])
    submit = SubmitField('Update Profile')

class ProfileImageForm(FlaskForm):
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed.')
    ])
    submit = SubmitField('Update Profile Image')
