from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional, URL

class ReviewForm(FlaskForm):
    """
    Form for adding or editing a movie review.
    """
    content = TextAreaField('Review', validators=[DataRequired(message="Please enter your review content.")])
    submit = SubmitField('Submit Review')

class MovieForm(FlaskForm):
    """
    Form for adding or editing a movie. Uses URL for cover image.
    """
    title = StringField('Title', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    genre = SelectField('Genre', choices=[
        ('action', 'Action'), ('adventure', 'Adventure'), ('animation', 'Animation'), ('comedy', 'Comedy'), ('drama', 'Drama'), ('fantasy', 'Fantasy'),('family', 'Family'), ('horror', 'Horror'), ('music', 'Music'), ('mystery', 'Mystery'), ('romance', 'Romance'), ('thriller', 'Thriller')
    ])
    director = StringField('Director', validators=[DataRequired()])
    overview = TextAreaField('Overview', validators=[DataRequired()])
    cast = TextAreaField('Cast', description="List the main cast. Separate names with commas.")
    cover_image = StringField('Cover Image URL', validators=[Optional(), URL(message='Invalid URL')])
    trailer_link = StringField('Trailer Link', validators=[
        DataRequired(message="Please provide a link to the movie trailer."),
        Regexp(regex=r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$',
               message="Please enter a valid URL.")])
    submit = SubmitField('Add Movie')

class RegistrationForm(FlaskForm):
    """
    Form for user registration. Uses URL for profile image.
    """
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
    profile_image = StringField('Profile Image URL', validators=[Optional(), URL(message='Invalid URL')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    username_or_email = StringField('Username or Email', validators=[DataRequired(message="Please enter your username or email.")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter your password.")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    """
    Form for updating user profile, including profile image URL.
    """
    username = StringField('Username', validators=[
        DataRequired(message="Please enter a username."),
        Length(min=4, max=25, message="Username must be between 4 and 25 characters.")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Please enter your email address."),
        Email(message="Please enter a valid email address.")
    ])
    profile_image = StringField('Profile Image URL', validators=[Optional(), URL(message='Invalid URL')])
    submit = SubmitField('Update Profile')

class ProfileImageForm(FlaskForm):
    """
    Form specifically for updating the profile image URL.
    """
    profile_image = StringField('Profile Image URL', validators=[Optional(), URL(message='Invalid URL')])
    submit = SubmitField('Update Profile Image')
