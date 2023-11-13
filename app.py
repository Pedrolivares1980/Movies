from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask import Flask, flash, render_template, redirect, request, url_for, send_from_directory
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf.csrf import CSRFProtect
from models import User, Movie, Review, db
import os
import random
from forms import RegistrationForm, LoginForm, MovieForm, ReviewForm, ProfileForm, ProfileImageForm

app = Flask(__name__)
app.config.from_object('config.Config')  # Load configuration from config.py based on the environment
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Define the route for unauthorized users to be redirected to

csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the session using the user ID.
    """
    return User.query.get(int(user_id))

# Initialize database within the application context
with app.app_context():
    db.init_app(app)
    db.create_all() 


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve the uploaded files from the uploads folder.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    """
    Home page route showing a random selection of movies.
    """
    all_movies = Movie.query.all()

    # Show a default image if there are no movies to display
    if not all_movies:
        default_image = url_for('static', filename='images/default_image.jpg')
        return render_template('index.html', default_image=default_image, random_movies=[])

    # Select a random subset of movies to display
    random_movies = random.sample(all_movies, min(8, len(all_movies)))
    return render_template('index.html', random_movies=random_movies)

@app.route('/movies')
def movies():
    genres = [genre for genre, _ in MovieForm().genre.choices]
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    genre_query = request.args.get('genre', '')

    # Filtro por género y búsqueda
    if search_query and genre_query:
        movies_query = Movie.query.filter(Movie.genre == genre_query, 
                                          Movie.title.ilike(f'%{search_query}%')).paginate(page=page, per_page=10)
    elif genre_query:
        movies_query = Movie.query.filter(Movie.genre == genre_query).paginate(page=page, per_page=10)
    elif search_query:
        movies_query = Movie.query.filter(Movie.title.ilike(f'%{search_query}%')).paginate(page=page, per_page=10)
    else:
        movies_query = Movie.query.paginate(page=page, per_page=10)

    return render_template('movies.html', movies=movies_query.items, 
                           search_query=search_query, pagination=movies_query, genres=genres)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for user registration. Handles both the display of the registration form
    and the registration logic upon form submission.
    """
    if current_user.is_authenticated:
        # Redirect to the index page if the user is already authenticated
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Form validation has passed
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data  # Password hashing is handled in the User model setter
        )

        if form.profile_image.data:
            # Save the profile image if one has been uploaded
            profile_image = form.profile_image.data
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.profile_image = filename

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for user login. Handles both the display of the login form
    and the login logic upon form submission.
    """
    if current_user.is_authenticated:
        # Redirect to the index page if the user is already logged in
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Form validation has passed
        user = User.query.filter_by(email=form.username_or_email.data).first() or \
               User.query.filter_by(username=form.username_or_email.data).first()

        if user and user.verify_password(form.password.data):
            # User exists and password is correct
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """
    Route to log out the current user.
    """
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/update_profile_image', methods=['POST'])
@login_required
def update_profile_image():
    form = ProfileImageForm()

    if form.validate_on_submit():
        # Verificar si se ha cargado una nueva imagen de perfil
        if form.profile_image.data:
            # Obtener la imagen actual para eliminarla más tarde, si no es la predeterminada
            current_image = current_user.profile_image

            # Guardar la nueva imagen
            profile_image = form.profile_image.data
            filename = secure_filename(profile_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(filepath)

            # Actualizar la imagen de perfil del usuario
            current_user.profile_image = filename

            # Eliminar la imagen antigua si no es la imagen de perfil predeterminada
            if current_image != 'default_profile.jpg':
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], current_image)
                if os.path.exists(old_image_path):
                    print("Ruta del archivo a eliminar:", old_image_path)
                    try:
                        os.remove(old_image_path)
                    except PermissionError as e:
                        print(f"Error de permiso al intentar eliminar el archivo: {e}")



            # Intentar actualizar la base de datos y manejar excepciones
            try:
                db.session.add(current_user)
                db.session.commit()
                flash('Profile image updated successfully.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while updating the profile image.', 'danger')
                print(f"Error: {e}")
        else:
            flash('No image selected.', 'danger')

    return redirect(url_for('profile'))



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile route where users can update their profile image and manage their content.
    """
    profile_form = ProfileForm()

    if profile_form.validate_on_submit():
        # Save the new profile image if it has been updated
        if profile_form.profile_image.data:
            profile_image = profile_form.profile_image.data
            filename = secure_filename(profile_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(filepath)
            current_user.profile_image = filename
            db.session.commit()
            flash('Profile image updated successfully.', 'success')

    # Get the movies and reviews by the current user
    user_movies = Movie.query.filter_by(user_id=current_user.id).all()
    user_reviews = Review.query.filter_by(user_id=current_user.id).all()

    # Check if the user has a profile image, otherwise use a default image
    if current_user.profile_image:
        profile_image_filename = current_user.profile_image
    else:
        # Use a default image filename or path
        profile_image_filename = 'default_profile_image.jpg'  # Adjust with your default image filename

    return render_template('profile.html', form=profile_form, user_movies=user_movies, user_reviews=user_reviews, user=current_user, filename=profile_image_filename)



# @app.route('/delete_account', methods=['POST'])
# @login_required
# def delete_account():
#     """
#     Route to handle the deletion of the user account. It will remove the user's movies,
#     reviews, and the account itself. A cascade delete is configured in the database models
#     to handle related records.
#     """
#     try:
#         # User data is deleted via cascade delete, so no need to manually remove movies or reviews
#         db.session.delete(current_user)
#         db.session.commit()
#         logout_user()
#         flash('Your account has been deleted, including all associated movies and reviews.', 'success')
#         return redirect(url_for('index'))
#     except Exception as e:
#         db.session.rollback()
#         app.logger.error(f'Error deleting account: {e}')
#         flash('An error occurred while deleting the account. Please try again.', 'danger')
#         return redirect(url_for('profile'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # Guardar el nombre de la imagen de perfil actual, si existe
    profile_image = current_user.profile_image

    try:
        # Eliminar la imagen de perfil, si existe
        if profile_image:
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image)
            if os.path.exists(profile_image_path):
                os.remove(profile_image_path)

        # Eliminar datos del usuario
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash('Your account has been deleted, including all associated movies and reviews.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting account: {e}')
        flash('An error occurred while deleting the account. Please try again.', 'danger')
        return redirect(url_for('profile'))


@app.route('/add_movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    """
    Route to add a new movie to the user's library. It handles the display and processing
    of the movie creation form.
    """
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
            user_id=current_user.id
        )

        if form.cover_image.data:
            cover_image = form.cover_image.data
            filename = secure_filename(cover_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            cover_image.save(filepath)
            new_movie.cover_image = filename
        else:
            new_movie.cover_image = None  # No asignar un valor por defecto aquí

        db.session.add(new_movie)
        db.session.commit()
        flash('Movie added successfully to your library!', 'success')
        return redirect(url_for('profile'))

    return render_template('add_movie.html', form=form)


@app.route('/edit_movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    """
    Route to edit an existing movie. It retrieves the movie by its ID and allows the user to update its details.
    """
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

        # Check if a new cover image has been uploaded
        if form.cover_image.data:
            new_cover_image = form.cover_image.data
            filename = secure_filename(new_cover_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            new_cover_image.save(filepath)

            # Delete old cover image if not default
            if movie.cover_image and movie.cover_image != 'default_cover.jpg':
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], movie.cover_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            movie.cover_image = filename

        db.session.commit()
        flash('Movie details updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_movie.html', form=form, movie=movie)

@app.route('/delete_movie/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash('You are not authorized to delete this movie.', 'danger')
        return redirect(url_for('profile'))

    # Eliminar la imagen asociada, si existe y no es la imagen por defecto
    if movie.cover_image and movie.cover_image != 'default_cover.jpg':
        cover_image_path = os.path.join(app.config['UPLOAD_FOLDER'], movie.cover_image)
        if os.path.exists(cover_image_path):
            try:
                os.remove(cover_image_path)
            except Exception as e:
                flash(f'Error al eliminar la imagen asociada: {e}', 'danger')
                return redirect(url_for('profile'))

    # Intentar eliminar la película y sus reseñas asociadas
    try:
        db.session.delete(movie)
        db.session.commit()
        flash('Movie deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the movie: {e}', 'danger')

    return redirect(url_for('profile'))



@app.route('/movie_details/<int:movie_id>')
def movie_details(movie_id):
    """
    Route to display the details of a movie along with its reviews.
    Users can view all information about a movie and read reviews from other users.
    """
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.date_posted.desc()).all()
    return render_template('movie_details.html', movie=movie, reviews=reviews)


@app.route('/add_review/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def add_review(movie_id):
    """
    Allow any authenticated user to add a review to a movie.
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
    Allow only the author of the review to edit it.
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

# @app.route('/add_review/<int:movie_id>', methods=['GET', 'POST'])
# @login_required
# def add_review(movie_id):
#     """
#     Route to add a review to a movie. It displays a form to submit a review and processes it upon submission.
#     """
#     form = ReviewForm()
#     movie = Movie.query.get_or_404(movie_id)

#     if form.validate_on_submit():
#         new_review = Review(content=form.content.data, movie_id=movie_id, user_id=current_user.id)
#         db.session.add(new_review)
#         db.session.commit()
#         flash('Your review has been added.', 'success')
#         return redirect(url_for('movie_details', movie_id=movie_id))

#     return render_template('add_review.html', form=form, movie=movie)


# @app.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
# @login_required
# def edit_review(review_id):
#     """
#     Route to edit a review. It checks if the current user is the author of the review
#     and allows them to update the content of their review.
#     """
#     review = Review.query.get_or_404(review_id)
#     # Ensure the current user is the author of the review
#     if review.user_id != current_user.id:
#         flash('You are not authorized to edit this review.', 'danger')
#         return redirect(url_for('index'))

#     form = ReviewForm(obj=review)
#     if form.validate_on_submit():
#         review.content = form.content.data
#         db.session.commit()
#         flash('Review updated successfully.', 'success')
#         return redirect(url_for('movie_details', movie_id=review.movie_id))

#     movie = Movie.query.get(review.movie_id)
#     return render_template('edit_review.html', form=form, review=review, movie=movie)

@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """
    Route to delete a review. It checks if the current user is the author of the review
    and then deletes it from the database.
    """
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash('You are not authorized to delete this review.', 'danger')
        return redirect(url_for('movie_details', movie_id=review.movie_id))
    
    db.session.delete(review)
    db.session.commit()
    flash('Review has been deleted.', 'success')
    return redirect(url_for('movie_details', movie_id=review.movie_id))


if __name__ == "__main__":
    app.run(debug=True)


