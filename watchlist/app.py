from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
import os
from movie_collection.models import movie_model
from movie_collection.models.watchlist_model import WatchlistModel
from movie_collection.utils.sql_utils import check_database_connection, check_table_exists
from movie_collection.models.user_model import Users
from config import ProductionConfig
from movie_collection.db import db
from movie_collection.models.tmdb_api_model import TMDbAPI


tmdb_api = TMDbAPI(api_key=os.getenv("TMDB_API_KEY"))

\


# Load environment variables from .env file
load_dotenv()

# app = Flask(__name__)

 

# watchlist_model = WatchlistModel()
def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    watchlist_model = WatchlistModel()


    ####################################################
    #
    # Healthchecks
    #
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)


    @app.route('/api/db-check', methods=['GET'])
    def db_check() -> Response:
        """
        Route to check if the database connection and movies table are functional.

        Returns:
            JSON response indicating the database health status.
        Raises:
            404 error if there is an issue with the database.
        """
        try:
            app.logger.info("Checking database connection...")
            check_database_connection()
            app.logger.info("Database connection is OK.")
            app.logger.info("Checking if movies table exists...")
            check_table_exists("movies")
            app.logger.info("movies table exists.")
            return make_response(jsonify({'database_status': 'healthy'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 404)



    ##########################################################
    #
    # User Management
    #
    ##########################################################

    @app.route('/api/create-account', methods=['POST'])
    def create_account() -> Response:
        """
        Route to create a new user account.
        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.
        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()
            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')
            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)
            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)
            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/api/update-password', methods=['PUT'])
    def update_password() -> Response:
        """
        Route to update a user's password.
        Expected JSON Input:
            - username (str): The username of the user to be updated.
            - password (str): The current password for the user to be updated.
        Returns:
            JSON response indicating the success of password modification.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue updating the user password from the database.
        """
        app.logger.info('Updating password')
        try:
            # Get the JSON data from the request
            data = request.get_json()
            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')
            if not username:
                return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)
            # Call the User function to delete the user from the database
            app.logger.info('Updateing user password: %s', username)
            Users.update_password(username, password)
            app.logger.info("User password updated: %s", username)
            return make_response(jsonify({'status': 'password updated', 'username': username}), 200)
        except Exception as e:
            app.logger.error("Failed to update user password: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)
        
    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Route to log in a user and load their combatants.
        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.
        Returns:
            JSON response indicating the success of the login.
        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")
        username = data['username']
        password = data['password']
        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")
            Users.login_user(username, password) 
            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200
        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


    ##########################################################
    #
    # Movie Management
    #
    ##########################################################

    @app.route('/api/create-movie', methods=['POST'])
    def add_movie() -> Response:
        """
        Route to add a new movie to the watchlist.

        Expected JSON Input:
            - director (str): The director's name.
            - title (str): The movie title.
            - year (int): The year the movie was released.
            - genre (str): The genre of the movie.
            - duration (int): The duration of the movie in minutes.
            - rating (float): The IMDb movie rating.

        Returns:
            JSON response indicating the success of the movie addition.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the movie to the watchlist.
        """
        app.logger.info('Adding a new movie to the catalog')
        try:
            data = request.get_json()

            director = data.get('director')
            title = data.get('title')
            year = data.get('year')
            genre = data.get('genre')
            duration = data.get('duration')
            rating = data.get('rating')

            if not director or not title or year is None or not genre or duration is None or rating is None:
                return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

            # Add the movie to the watchlist
            app.logger.info('Creating movie: %s - %s', director, title)
            movie_model.create_movie(director=director, title=title, year=year, genre=genre, duration=duration, rating=rating)
            app.logger.info("Movie created: %s - %s", director, title)
            return make_response(jsonify({'status': 'success', 'movie': title}), 201)
        except Exception as e:
            app.logger.error("Failed to add movie: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/clear-catalog', methods=['DELETE'])
    def clear_catalog() -> Response:
        """
        Route to clear the entire movie catalog (recreates the table).

        Returns:
            JSON response indicating success of the operation or error message.
        """
        try:
            app.logger.info("Clearing the movie catalog")
            movie_model.clear_catalog()
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Error clearing catalog: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/delete-movie/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id: int) -> Response:
        """
        Route to delete a movie by its ID (soft delete).

        Path Parameter:
            - movie_id (int): The ID of the movie to delete.

        Returns:
            JSON response indicating success of the operation or error message.
        """
        try:
            app.logger.info(f"Deleting movie by ID: {movie_id}")
            movie_model.delete_movie(movie_id)
            return make_response(jsonify({'status': 'movie deleted'}), 200)
        except Exception as e:
            app.logger.error(f"Error deleting movie: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/get-all-movies-from-catalog', methods=['GET'])
    def get_all_movies() -> Response:
        """
        Route to retrieve all movies in the catalog (non-deleted), with an option to sort by watch count or rating.

        Query Parameter:
            - sort_by_rating (bool, optional): If true, sort movies by rating in descending order.
            - sort_by_watch_count (bool, optional): If true, sort movies by watch count.

        Returns:
            JSON response with the list of movies or error message.
        """
        try:
            # Extract query parameter for sorting by watch count
            sort_by_rating = request.args.get('sort_by_rating', 'false').lower() == 'true'
            sort_by_watch_count = request.args.get('sort_by_watch_count', 'false').lower() == 'true'

            app.logger.info("Retrieving all movies from the watchlist, sort_by_rating=%s, sort_by_watch_count=%s",
                            sort_by_rating, sort_by_watch_count)
                            
            # Get movies from the model
            app.logger.info("Getting all movies in the watchlist from movie_model")
            movies = movie_model.get_all_movies_movie_model(sort_by_rating=sort_by_rating, sort_by_watch_count=sort_by_watch_count)

            return make_response(jsonify({'status': 'success', 'movies': movies}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving movies: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/get-movie-from-catalog-by-id/<int:movie_id>', methods=['GET'])
    def get_movie_by_id(movie_id: int) -> Response:
        """
        Route to retrieve a movie by its ID.

        Path Parameter:
            - movie_id (int): The ID of the movie.

        Returns:
            JSON response with the movie details or error message.
        """
        try:
            app.logger.info(f"Retrieving movie by ID: {movie_id}")
            movie = movie_model.get_movie_by_id(movie_id)
            return make_response(jsonify({'status': 'success', 'movie': movie}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving movie by ID: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-movie-from-catalog-by-compound-key', methods=['GET'])
    def get_movie_by_compound_key() -> Response:
        """
        Route to retrieve a movie by its compound key (director, title, year).

        Query Parameters:
            - director (str): The director's name.
            - title (str): The movie title.
            - year (int): The year the movie was released.

        Returns:
            JSON response with the movie details or error message.
        """
        try:
            # Extract query parameters from the request
            director = request.args.get('director')
            title = request.args.get('title')
            year = request.args.get('year')

            if not director or not title or not year:
                return make_response(jsonify({'error': 'Missing required query parameters: director, title, year'}), 400)

            # Attempt to cast year to an integer
            try:
                year = int(year)
            except ValueError:
                return make_response(jsonify({'error': 'Year must be an integer'}), 400)

            app.logger.info(f"Retrieving movie by compound key: {director}, {title}, {year}")
            movie = movie_model.get_movie_by_compound_key(director, title, year)
            return make_response(jsonify({'status': 'success', 'movie': movie}), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving movie by compound key: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-random-movie', methods=['GET'])
    def get_random_movie() -> Response:
        """
        Route to retrieve a random movie from the catalog.

        Returns:
            JSON response with the details of a random movie or error message.
        """
        try:
            app.logger.info("Retrieving a random movie from the catalog")
            movie = movie_model.get_random_movie()
            return make_response(jsonify({'status': 'success', 'movie': movie}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving a random movie: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    ############################################################
    #
    # Watchlist Management
    #
    ############################################################

    @app.route('/api/add-movie-to-watchlist', methods=['POST'])
    def add_movie_to_watchlist() -> Response:
        """
        Route to add a movie to the watchlist by compound key (director, title, year).

        Expected JSON Input:
            - director (str): The director's name.
            - title (str): The movie title.
            - year (int): The year the movie was released.

        Returns:
            JSON response indicating success of the addition or error message.
        """
        try:
            data = request.get_json()

            director = data.get('director')
            title = data.get('title')
            year = data.get('year')

            if not director or not title or not year:
                return make_response(jsonify({'error': 'Invalid input. Director, title, and year are required.'}), 400)

            # Lookup the movie by compound key
            movie = movie_model.get_movie_by_compound_key(director, title, year)

            # Add movie to watchlist
            watchlist_model.add_movie_to_watchlist(movie)

            app.logger.info(f"Movie added to watchlist: {director} - {title} ({year})")
            return make_response(jsonify({'status': 'success', 'message': 'Movie added to watchlist'}), 201)

        except Exception as e:
            app.logger.error(f"Error adding movie to watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/remove-movie-from-watchlist', methods=['DELETE'])
    def remove_movie_by_movie_id() -> Response:
        """
        Route to remove a movie from the watchlist by compound key (director, title, year).

        Expected JSON Input:
            - director (str): The director's name.
            - title (str): The movie title.
            - year (int): The year the movie was released.

        Returns:
            JSON response indicating success of the removal or error message.
        """
        try:
            data = request.get_json()

            director = data.get('director')
            title = data.get('title')
            year = data.get('year')

            if not director or not title or not year:
                return make_response(jsonify({'error': 'Invalid input. Director, title, and year are required.'}), 400)

            # Lookup the movie by compound key
            movie = movie_model.get_movie_by_compound_key(director, title, year)

            # Remove movie from watchlist
            watchlist_model.remove_movie_by_movie_id(movie.id)

            app.logger.info(f"Movie removed from watchlist: {director} - {title} ({year})")
            return make_response(jsonify({'status': 'success', 'message': 'Movie removed from watchlist'}), 200)

        except Exception as e:
            app.logger.error(f"Error removing movie from watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/remove-movie-from-watchlist-by-film-number/<int:film_number>', methods=['DELETE'])
    def remove_movie_by_film_number(film_number: int) -> Response:
        """
        Route to remove a movie from the watchlist by film number.

        Path Parameter:
            - film_number (int): The film number of the movie to remove.

        Returns:
            JSON response indicating success of the removal or an error message.
        """
        try:
            app.logger.info(f"Removing movie from watchlist by film number: {film_number}")

            # Remove movie by film number
            watchlist_model.remove_movie_by_film_number(film_number)

            return make_response(jsonify({'status': 'success', 'message': f'Movie at film number {film_number} removed from watchlist'}), 200)

        except ValueError as e:
            app.logger.error(f"Error removing movie by film number: {e}")
            return make_response(jsonify({'error': str(e)}), 404)
        except Exception as e:
            app.logger.error(f"Error removing movie from watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/clear-watchlist', methods=['POST'])
    def clear_watchlist() -> Response:
        """
        Route to clear all movies from the watchlist.

        Returns:
            JSON response indicating success of the operation or an error message.
        """
        try:
            app.logger.info('Clearing the watchlist')

            # Clear the entire watchlist
            watchlist_model.clear_watchlist()

            return make_response(jsonify({'status': 'success', 'message': 'Watchlist cleared'}), 200)

        except Exception as e:
            app.logger.error(f"Error clearing the watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    ############################################################
    # 
    # TMBD Management
    #
    ############################################################
    @app.route('/api/movies-by-director', methods=['GET'])
    def movies_by_director():
        director_name = request.args.get('director')
        if not director_name:
            return jsonify({"error": "Director name is required"}), 400
        movies = tmdb_api.get_movies_by_director(director_name)
        return jsonify({"movies": movies})

    @app.route('/api/top-rated-movies', methods=['GET'])
    def top_rated_movies():
        movies = tmdb_api.get_top_rated_movies()
        return jsonify({"movies": movies})

    @app.route('/api/search-movies', methods=['GET'])
    def search_movies():
        title = request.args.get('title')
        if not title:
            return jsonify({"error": "Movie title is required"}), 400
        movies = tmdb_api.search_movie_by_title(title)
        return jsonify({"movies": movies})

    @app.route('/api/movie-details/<int:movie_id>', methods=['GET'])
    def movie_details(movie_id):
        details = tmdb_api.get_movie_details(movie_id)
        return jsonify({"movie": details})


    ############################################################
    #
    # Play Watchlist
    #
    ############################################################

    @app.route('/api/play-current-movie', methods=['POST'])
    def play_current_movie() -> Response:
        """
        Route to play the current movie in the watchlist.

        Returns:
            JSON response indicating success of the operation.
        Raises:
            500 error if there is an issue playing the current movie.
        """
        try:
            app.logger.info('Playing current movie')
            current_movie = watchlist_model.get_current_movie()
            watchlist_model.play_current_movie()

            return make_response(jsonify({
                'status': 'success',
                'movie': {
                    'id': current_movie.id,
                    'director': current_movie.director,
                    'title': current_movie.title,
                    'year': current_movie.year,
                    'genre': current_movie.genre,
                    'duration': current_movie.duration,
                    'rating': current_movie.rating
                }
            }), 200)
        except Exception as e:
            app.logger.error(f"Error playing current movie: {e}")
            return make_response(jsonify({'error': str(e)}), 500)


    @app.route('/api/play-entire-watchlist', methods=['POST'])
    def play_entire_watchlist() -> Response:
        """
        Route to play all movies in the watchlist.

        Returns:
            JSON response indicating success of the operation.
        Raises:
            500 error if there is an issue playing the watchlist.
        """
        try:
            app.logger.info('Playing entire watchlist')
            watchlist_model.play_entire_watchlist()
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Error playing watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/play-rest-of-watchlist', methods=['POST'])
    def play_rest_of_watchlist() -> Response:
        """
        Route to play the rest of the watchlist from the current track.

        Returns:
            JSON response indicating success of the operation.
        Raises:
            500 error if there is an issue playing the rest of the watchlist.
        """
        try:
            app.logger.info('Playing rest of the watchlist')
            watchlist_model.play_rest_of_watchlist()
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Error playing rest of the watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/rewind-watchlist', methods=['POST'])
    def rewind_watchlist() -> Response:
        """
        Route to rewind the watchlist to the first movie.

        Returns:
            JSON response indicating success of the operation.
        Raises:
            500 error if there is an issue rewinding the watchlist.
        """
        try:
            app.logger.info('Rewinding watchlist to the first movie')
            watchlist_model.rewind_watchlist()
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Error rewinding watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-all-movies-from-watchlist', methods=['GET'])
    def get_all_movies_from_watchlist() -> Response:
        """
        Route to retrieve all movies in the watchlist.

        Returns:
            JSON response with the list of movies or an error message.
        """
        try:
            app.logger.info("Retrieving all movies from the watchlist")

            # Get all movies from the watchlist
            movies = watchlist_model.get_all_movies()

            return make_response(jsonify({'status': 'success', 'movies': movies}), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving movies from watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-movie-from-watchlist-by-film-number/<int:film_number>', methods=['GET'])
    def get_movie_by_film_number(film_number: int) -> Response:
        """
        Route to retrieve a movie by its film number from the watchlist.

        Path Parameter:
            - film_number (int): The film number of the movie.

        Returns:
            JSON response with the movie details or error message.
        """
        try:
            app.logger.info(f"Retrieving movie from watchlist by film number: {film_number}")

            # Get the movie by film number
            movie = watchlist_model.get_movie_by_film_number(film_number)

            return make_response(jsonify({'status': 'success', 'movie': movie}), 200)

        except ValueError as e:
            app.logger.error(f"Error retrieving movie by film number: {e}")
            return make_response(jsonify({'error': str(e)}), 404)
        except Exception as e:
            app.logger.error(f"Error retrieving movie from watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-current-movie', methods=['GET'])
    def get_current_movie() -> Response:
        """
        Route to retrieve the current movie being played.

        Returns:
            JSON response with the current movie details or error message.
        """
        try:
            app.logger.info("Retrieving the current movie from the watchlist")

            # Get the current movie
            current_movie = watchlist_model.get_current_movie()

            return make_response(jsonify({'status': 'success', 'current_movie': current_movie}), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving current movie: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-watchlist-length-duration', methods=['GET'])
    def get_watchlist_length_and_duration() -> Response:
        """
        Route to retrieve both the length (number of movies) and the total duration of the watchlist.

        Returns:
            JSON response with the watchlist length and total duration or error message.
        """
        try:
            app.logger.info("Retrieving watchlist length and total duration")

            # Get watchlist length and duration
            watchlist_length = watchlist_model.get_watchlist_length()
            watchlist_duration = watchlist_model.get_watchlist_duration()

            return make_response(jsonify({
                'status': 'success',
                'watchlist_length': watchlist_length,
                'watchlist_duration': watchlist_duration
            }), 200)

        except Exception as e:
            app.logger.error(f"Error retrieving watchlist length and duration: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/go-to-film-number/<int:film_number>', methods=['POST'])
    def go_to_film_number(film_number: int) -> Response:
        """
        Route to set the watchlist to start playing from a specific film number.

        Path Parameter:
            - film_number (int): The film number to set as the current movie.

        Returns:
            JSON response indicating success or an error message.
        """
        try:
            app.logger.info(f"Going to film number: {film_number}")

            # Set the watchlist to start at the given film number
            watchlist_model.go_to_film_number(film_number)

            return make_response(jsonify({'status': 'success', 'film_number': film_number}), 200)
        except ValueError as e:
            app.logger.error(f"Error going to film number {film_number}: {e}")
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Error going to film number: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    ############################################################
    #
    # Arrange Watchlist
    #
    ############################################################

    @app.route('/api/move-movie-to-beginning', methods=['POST'])
    def move_movie_to_beginning() -> Response:
        """
        Route to move a movie to the beginning of the watchlist.

        Expected JSON Input:
            - director (str): The director of the movie.
            - title (str): The title of the movie.
            - year (int): The year the movie was released.

        Returns:
            JSON response indicating success or an error message.
        """
        try:
            data = request.get_json()

            director = data.get('director')
            title = data.get('title')
            year = data.get('year')

            app.logger.info(f"Moving movie to beginning: {director} - {title} ({year})")

            # Retrieve movie by compound key and move it to the beginning
            movie = movie_model.get_movie_by_compound_key(director, title, year)
            watchlist_model.move_movie_to_beginning(movie.id)

            return make_response(jsonify({'status': 'success', 'movie': f'{director} - {title}'}), 200)
        except Exception as e:
            app.logger.error(f"Error moving movie to beginning: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/move-movie-to-end', methods=['POST'])
    def move_movie_to_end() -> Response:
        """
        Route to move a movie to the end of the watchlist.

        Expected JSON Input:
            - director (str): The director of the movie.
            - title (str): The title of the movie.
            - year (int): The year the movie was released.

        Returns:
            JSON response indicating success or an error message.
        """
        try:
            data = request.get_json()

            director = data.get('director')
            title = data.get('title')
            year = data.get('year')

            app.logger.info(f"Moving movie to end: {director} - {title} ({year})")

            # Retrieve movie by compound key and move it to the end
            movie = movie_model.get_movie_by_compound_key(director, title, year)
            watchlist_model.move_movie_to_end(movie.id)

            return make_response(jsonify({'status': 'success', 'movie': f'{director} - {title}'}), 200)
        except Exception as e:
            app.logger.error(f"Error moving movie to end: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/move-movie-to-film-number', methods=['POST'])
    def move_movie_to_film_number() -> Response:
        """
        Route to move a movie to a specific film number in the watchlist.

        Expected JSON Input:
            - director (str): The director of the movie.
            - title (str): The title of the movie.
            - year (int): The year the movie was released.
            - film_number (int): The new film number to move the movie to.

        Returns:
            JSON response indicating success or an error message.
        """
        try:
            data = request.get_json()

            director = data.get('director')
            title = data.get('title')
            year = data.get('year')
            film_number = data.get('film_number')

            app.logger.info(f"Moving movie to film number {film_number}: {director} - {title} ({year})")

            # Retrieve movie by compound key and move it to the specified film number
            movie = movie_model.get_movie_by_compound_key(director, title, year)
            if not movie:
                app.logger.error(f"Movie not found with provided details: {director}, {title}, {year}")
                raise ValueError("Movie not found")
            watchlist_model.move_movie_to_film_number(movie.id, film_number)

            return make_response(jsonify({'status': 'success', 'movie': f'{director} - {title}', 'film_number': film_number}), 200)
        except Exception as e:
            app.logger.error(f"Error moving movie to film number: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/swap-movies-in-watchlist', methods=['POST'])
    def swap_movies_in_watchlist() -> Response:
        """
        Route to swap two movies in the watchlist by their film numbers.

        Expected JSON Input:
            - film_number_1 (int): The film number of the first movie.
            - film_number_2 (int): The film number of the second movie.

        Returns:
            JSON response indicating success or an error message.
        """
        try:
            data = request.get_json()

            film_number_1 = data.get('film_number_1')
            film_number_2 = data.get('film_number_2')

            app.logger.info(f"Swapping movies at film numbers {film_number_1} and {film_number_2}")

            # Retrieve movies by film numbers and swap them
            movie_1 = watchlist_model.get_movie_by_film_number(film_number_1)
            movie_2 = watchlist_model.get_movie_by_film_number(film_number_2)
            watchlist_model.swap_movies_in_watchlist(movie_1.id, movie_2.id)

            return make_response(jsonify({
                'status': 'success',
                'swapped_movies': {
                    'film_1': {'id': movie_1.id, 'director': movie_1.director, 'title': movie_1.title},
                    'film_2': {'id': movie_2.id, 'director': movie_2.director, 'title': movie_2.title}
                }
            }), 200)
        except Exception as e:
            app.logger.error(f"Error swapping movies in watchlist: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    ############################################################
    #
    # Leaderboard / Stats
    #
    ############################################################

    @app.route('/api/movie-leaderboard', methods=['GET'])
    def get_movie_leaderboard() -> Response:
        """
        Route to get a list of all sorted by watch count or rating.

        Query Parameters:
            - sort_by_rating (bool, optional): If true, sort by rating in descending order.
            - sort_by_watch_count (bool, optional): If true, sort by watch count in descending order.

        Returns:
            JSON response with a sorted leaderboard of movies.
        Raises:
            500 error if there is an issue generating the leaderboard.
        """
    #     try:
    #         app.logger.info("Generating movie leaderboard sorted")
    #         leaderboard_data = movie_model.get_all_movies(sort_by_watch_count=True)
    #         return make_response(jsonify({'status': 'success', 'leaderboard': leaderboard_data}), 200)
    #     except Exception as e:
    #         app.logger.error(f"Error generating leaderboard: {e}")
    #         return make_response(jsonify({'error': str(e)}), 500)


        try:
            # Extract sorting preferences from query parameters
            sort_by_rating = request.args.get('sort_by_rating', 'false').lower() == 'true'
            sort_by_watch_count = request.args.get('sort_by_watch_count', 'false').lower() == 'true'

            app.logger.info("Generating movie leaderboard sorted by rating=%s, watch_count=%s",
                            sort_by_rating, sort_by_watch_count)

            # Fetch sorted movies from the model
            leaderboard_data = movie_model.get_all_movies_movie_model(sort_by_rating=sort_by_rating,
                                                        sort_by_watch_count=sort_by_watch_count)

            return make_response(jsonify({'status': 'success', 'leaderboard': leaderboard_data}), 200)

        except Exception as e:
            app.logger.error(f"Error generating leaderboard: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)