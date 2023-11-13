from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask import Flask, flash, render_template, redirect, request, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf.csrf import CSRFProtect
from models import User, Movie, Review, db
from forms import RegistrationForm, LoginForm, MovieForm, ReviewForm, ProfileForm, ProfileImageForm
import random

app = Flask(__name__)
app.config.from_object('config.Config')  # Load configuration from config.py
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    """Load a user from the session using the user ID."""
    return User.query.get(int(user_id))

# Initialize database within the application context
with app.app_context():
    db.init_app(app)
    db.create_all()

@app.route('/')
def index():
    """Home page route showing a random selection of movies."""
    all_movies = Movie.query.all()
    if not all_movies:
        default_image = url_for('static', filename='images/default_image.jpg')
        return render_template('index.html', default_image=default_image, random_movies=[])

    random_movies = random.sample(all_movies, min(8, len(all_movies)))
    return render_template('index.html', random_movies=random_movies)

@app.route('/movies')
def movies():
    """Route for listing movies with filters for search and genre."""
    genres = [genre for genre, _ in MovieForm().genre.choices]
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    genre_query = request.args.get('genre', '')

    movies_query = Movie.query
    if genre_query:
        movies_query = movies_query.filter(Movie.genre == genre_query)
    if search_query:
        movies_query = movies_query.filter(Movie.title.ilike(f'%{search_query}%'))
    movies_query = movies_query.paginate(page=page, per_page=10)

    return render_template('movies.html', movies=movies_query.items, search_query=search_query, pagination=movies_query, genres=genres)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Route for user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        user.profile_image = form.profile_image.data  # Directly save the URL
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Route for user login."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.email == form.username_or_email.data) | (User.username == form.username_or_email.data)).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Route to log out the current user."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/update_profile_image', methods=['POST'])
@login_required
def update_profile_image():
    """Route to update the current user's profile image with a URL."""
    form = ProfileImageForm()
    if form.validate_on_submit():
        current_user.profile_image = form.profile_image.data
        db.session.commit()
        flash('Profile image updated successfully.', 'success')
    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile route for updates and managing content."""
    profile_form = ProfileForm()
    if profile_form.validate_on_submit():
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.profile_image = profile_form.profile_image.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')

    user_movies = Movie.query.filter_by(user_id=current_user.id).all()
    user_reviews = Review.query.filter_by(user_id=current_user.id).all()

    return render_template('profile.html', form=profile_form, user_movies=user_movies, user_reviews=user_reviews, user=current_user)

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Route to handle the deletion of the user account and associated data."""
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('index'))

@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    """Route to add a new movie to the user's library."""
    form = MovieForm()
    if form.validate_on_submit():
        new_movie = Movie(
            title=form.title.data,
            year=form.year.data,
            genre=form.genre.data,
            director=form.director.data,
            overview=form.overview.data,
            trailer_link=form.trailer_link.data,
            cast=form.cast.data,
            cover_image=form.cover_image.data,  # Directly save the URL
            user_id=current_user.id
        )
        db.session.add(new_movie)
        db.session.commit()
        flash('Movie added successfully to your library!', 'success')
        return redirect(url_for('profile'))

    return render_template('add_movie.html', form=form)

@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    """Route to edit an existing movie."""
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash('You are not authorized to edit this movie.', 'danger')
        return redirect(url_for('profile'))

    form = MovieForm(obj=movie)
    if form.validate_on_submit():
        movie.title = form.title.data
        movie.year = form.year.data
        movie.genre = form.genre.data
        movie.director = form.director.data
        movie.overview = form.overview.data
        movie.trailer_link = form.trailer_link.data
        movie.cast = form.cast.data
        movie.cover_image = form.cover_image.data
        db.session.commit()
        flash('Movie details updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_movie.html', form=form, movie=movie)

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    """Route to delete a movie from the user's library."""
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash('You are not authorized to delete this movie.', 'danger')
        return redirect(url_for('profile'))

    db.session.delete(movie)
    db.session.commit()
    flash('Movie deleted successfully.', 'success')
    return redirect(url_for('profile'))

@app.route('/movie_details/<int:movie_id>')
def movie_details(movie_id):
    """
    Route to display the details of a movie along with its reviews.
    """
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.date_posted.desc()).all()
    return render_template('movie_details.html', movie=movie, reviews=reviews)

@app.route('/add_review/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def add_review(movie_id):
    """
    Allow authenticated users to add a review for a movie.
    """
    form = ReviewForm()
    movie = Movie.query.get_or_404(movie_id)
    if form.validate_on_submit():
        new_review = Review(content=form.content.data, movie_id=movie_id, user_id=current_user.id)
        db.session.add(new_review)
        db.session.commit()
        flash('Your review has been added.', 'success')
        return redirect(url_for('movie_details', movie_id=movie_id))

    return render_template('add_review.html', form=form, movie=movie)

@app.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """
    Allow the author of a review to edit it.
    """
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash('You are not authorized to edit this review.', 'danger')
        return redirect(url_for('index'))

    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        review.content = form.content.data
        db.session.commit()
        flash('Review updated successfully.', 'success')
        return redirect(url_for('movie_details', movie_id=review.movie_id))

    movie = Movie.query.get(review.movie_id)
    return render_template('edit_review.html', form=form, review=review, movie=movie)

@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """
    Route to delete a review written by the current user.
    """
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash('You are not authorized to delete this review.', 'danger')
        return redirect(url_for('movie_details', movie_id=review.movie_id))

    db.session.delete(review)
    db.session.commit()
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('movie_details', movie_id=review.movie_id))

if __name__ == "__main__":
    app.run(debug=True)
