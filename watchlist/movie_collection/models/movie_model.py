from dataclasses import dataclass
import logging
import os
import sqlite3

from movie_collection.utils.logger import configure_logger
from movie_collection.utils.random_utils import get_random
from movie_collection.utils.sql_utils import get_db_connection


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Movie:
    id: int
    director: str
    title: str
    year: int
    genre: str
    duration: int  # in minutes
    rating: float  #IMDb score out of 10.0

    def __post_init__(self):
        if self.duration <= 0:
            raise ValueError(f"Duration must be greater than 0, got {self.duration}")
        if (self.rating < 0.0) or (self.rating > 10.0):
            raise ValueError(f"Rating must be between 0.0 and 10.0, got {self.rating}")


def create_movie(director: str, title: str, year: int, genre: str, duration: int, rating: float) -> None:
    """
    Creates a new movie in the movies table.

    Args:
        director (str): The director's name.
        title (str): The movie title.
        year (int): The year the movie was released.
        genre (str): The movie genre.
        duration (int): The duration of the movie in minutes.
        rating (float): The IMDb movie rating out of 10.0.

    Raises:
        ValueError: If duration or rating are invalid.
        sqlite3.IntegrityError: If a movie with the same compound key (director, title, year) already exists.
        sqlite3.Error: For any other database errors.
    """
    # Validate the required fields
    if not isinstance(rating, float) or rating < 0.0 or rating > 10.0:
        raise ValueError(f"Invalid rating provided: {rating} (must be a float between 0.0 and 10.0).")
    if not isinstance(duration, int) or duration <= 0:
        raise ValueError(f"Invalid movie duration: {duration} (must be a positive integer).")
    if not isinstance(year, int) or year < 0:
        raise ValueError(f"Invalid year provided: {year} (must be a positive integer).")
    try:
        # Use the context manager to handle the database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO movies (director, title, year, genre, duration, rating)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (director, title, year, genre, duration, rating))
            conn.commit()

            logger.info("Movie created successfully: %s - %s (%d)", director, title, year)

    except sqlite3.IntegrityError as e:
        logger.error("Movie with director '%s', title '%s', and year %d already exists.", director, title, year)
        raise ValueError(f"Movie with director '{director}', title '{title}', and year {year} already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating movie: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")

def clear_catalog() -> None:
    """
    Recreates the movie table, effectively deleting all movies.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with open(os.getenv("SQL_CREATE_TABLE_PATH", "/app/sql/create_movie_table.sql"), "r") as fh:
            create_table_script = fh.read()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_script)
            conn.commit()

            logger.info("Catalog cleared successfully.")

    except sqlite3.Error as e:
        logger.error("Database error while clearing catalog: %s", str(e))
        raise e

def delete_movie(movie_id: int) -> None:
    """
    Soft deletes a movie from the catalog by marking it as deleted.

    Args:
        movie_id (int): The ID of the movie to delete.

    Raises:
        ValueError: If the movie with the given ID does not exist or is already marked as deleted.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the movie exists and if it's already deleted
            cursor.execute("SELECT deleted FROM movies WHERE id = ?", (movie_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Movie with ID %s has already been deleted", movie_id)
                    raise ValueError(f"Movie with ID {movie_id} has already been deleted")
            except TypeError:
                logger.info("Movie with ID %s not found", movie_id)
                raise ValueError(f"Movie with ID {movie_id} not found")

            # Perform the soft delete by setting 'deleted' to TRUE
            cursor.execute("UPDATE movies SET deleted = TRUE WHERE id = ?", (movie_id,))
            conn.commit()

            logger.info("Movie with ID %s marked as deleted.", movie_id)

    except sqlite3.Error as e:
        logger.error("Database error while deleting movie: %s", str(e))
        raise e

def get_movie_by_id(movie_id: int) -> Movie:
    """
    Retrieves a movie from the catalog by its movie ID.

    Args:
        movie_id (int): The ID of the movie to retrieve.

    Returns:
        Movie: The Movie object corresponding to the movie_id.

    Raises:
        ValueError: If the movie is not found or is marked as deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve movie with ID %s", movie_id)
            cursor.execute("""
                SELECT id, director, title, year, genre, duration, rating, deleted
                FROM movies
                WHERE id = ?
            """, (movie_id,))
            row = cursor.fetchone()

            if row:
                if row[7]:  # deleted flag
                    logger.info("Movie with ID %s has been deleted", movie_id)
                    raise ValueError(f"Movie with ID {movie_id} has been deleted")
                logger.info("Movie with ID %s found", movie_id)
                return Movie(id=row[0], director=row[1], title=row[2], year=row[3], genre=row[4], duration=row[5], rating=row[6])
            else:
                logger.info("Movie with ID %s not found", movie_id)
                raise ValueError(f"Movie with ID {movie_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving movie by ID %s: %s", movie_id, str(e))
        raise e

def get_movie_by_compound_key(director: str, title: str, year: int) -> Movie:
    """
    Retrieves a movie from the catalog by its compound key (director, title, year).

    Args:
        director (str): The director of the movie.
        title (str): The title of the movie.
        year (int): The year of the movie.

    Returns:
        Movie: The Movie object corresponding to the compound key.

    Raises:
        ValueError: If the movie is not found or is marked as deleted.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve movie with director '%s', title '%s', and year %d", director, title, year)
            cursor.execute("""
                SELECT id, director, title, year, genre, duration, rating, deleted
                FROM movies
                WHERE director = ? AND title = ? AND year = ?
            """, (director, title, year))
            row = cursor.fetchone()

            if row:
                if row[7]:  # deleted flag
                    logger.info("Movie with director '%s', title '%s', and year %d has been deleted", director, title, year)
                    raise ValueError(f"Movie with director '{director}', title '{title}', and year {year} has been deleted")
                logger.info("Movie with director '%s', title '%s', and year %d found", director, title, year)
                return Movie(id=row[0], director=row[1], title=row[2], year=row[3], genre=row[4], duration=row[5], rating=row[6])
            else:
                logger.info("Movie with director '%s', title '%s', and year %d not found", director, title, year)
                raise ValueError(f"Movie with director '{director}', title '{title}', and year {year} not found")

    except sqlite3.Error as e:
        logger.error("Database error while retrieving movie by compound key (director '%s', title '%s', year %d): %s", director, title, year, str(e))
        raise e

def get_all_movies(sort_by_rating: bool = False, sort_by_watch_count: bool = False) -> list[dict]:
    """
    Retrieves all movies that are not marked as deleted from the catalog.

    Args:
        sort_by_rating (bool): If true, sort movies by rating in descending order.
        sort_by_watch_count (bool): If True, sort the movies by watch count in descending order.

    Returns:
        list[dict]: A list of dictionaries representing all non-deleted movies in watchlist.

    Logs:
        Warning: If the catalog is empty.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to retrieve all non-deleted movies from the catalog")

            # # Determine the sort order based on the 'sort_by_watch_count' flag
            # query = """
            #     SELECT id, director, title, year, genre, duration, rating, watch_count
            #     FROM movies
            #     WHERE deleted = FALSE
            # """
            # if sort_by_watch_count:
            #     query += " ORDER BY watch_count DESC"

            # cursor.execute(query)
            # rows = cursor.fetchall()

            # if not rows:
            #     logger.warning("The movie catalog is empty.")
            #     return []

            # movies = [
            #     {
            #         "id": row[0],
            #         "director": row[1],
            #         "title": row[2],
            #         "year": row[3],
            #         "genre": row[4],
            #         "duration": row[5],
            #         "rating": row[6],
            #         "watch_count": row[7],

            #     }
            #     for row in rows
            # ]

            # Base query for retrieving all movies
            query = """
                SELECT id, director, title, year, genre, duration, rating, watch_count
                FROM movies
                WHERE deleted = FALSE
            """

            # Construct ORDER BY clause based on sorting parameters
            sort_clauses = []
            if sort_by_rating:
                sort_clauses.append("rating DESC")
            if sort_by_watch_count:
                sort_clauses.append("watch_count DESC")

            # Add ORDER BY clause if any sorting is specified
            if sort_clauses:
                query += " ORDER BY " + ", ".join(sort_clauses)

            logger.debug("Executing query: %s", query)

            cursor.execute(query)
            rows = cursor.fetchall()

            if not rows:
                logger.warning("The movie catalog is empty.")
                return []

            # Map query results to a list of dictionaries
            movies = [
                {
                    "id": row[0],
                    "director": row[1],
                    "title": row[2],
                    "year": row[3],
                    "genre": row[4],
                    "duration": row[5],
                    "rating": row[6],
                    "watch_count": row[7],
                }
                for row in rows
            ]
            logger.info("Retrieved %d movies from the catalog", len(movies))
            return movies

    except sqlite3.Error as e:
        logger.error("Database error while retrieving all movies: %s", str(e))
        raise e

def get_random_movie() -> Movie:
    """
    Retrieves a random movie from the catalog.

    Returns:
        Movie: A randomly selected Movie object.

    Raises:
        ValueError: If the catalog is empty.
    """
    try:
        all_movies = get_all_movies()

        if not all_movies:
            logger.info("Cannot retrieve random movie because the movie catalog is empty.")
            raise ValueError("The movie catalog is empty.")

        # Get a random index using the random.org API
        random_index = get_random(len(all_movies))
        logger.info("Random index selected: %d (total movies: %d)", random_index, len(all_movies))

        # Return the movie at the random index, adjust for 0-based indexing
        movie_data = all_movies[random_index - 1]
        return Movie(
            id=movie_data["id"],
            director=movie_data["director"],
            title=movie_data["title"],
            year=movie_data["year"],
            genre=movie_data["genre"],
            duration=movie_data["duration"],
            rating=movie_data["rating"]
        )

    except Exception as e:
        logger.error("Error while retrieving random movie: %s", str(e))
        raise e

def update_watch_count(movie_id: int) -> None:
    """
    Increments the watch count of a movie by movie ID.

    Args:
        movie_id (int): The ID of the movie whose watch count should be incremented.

    Raises:
        ValueError: If the movie does not exist or is marked as deleted.
        sqlite3.Error: If there is a database error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to update watch count for movie with ID %d", movie_id)

            # Check if the movie exists and if it's deleted
            cursor.execute("SELECT deleted FROM movies WHERE id = ?", (movie_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Movie with ID %d has been deleted", movie_id)
                    raise ValueError(f"Movie with ID {movie_id} has been deleted")
            except TypeError:
                logger.info("Movie with ID %d not found", movie_id)
                raise ValueError(f"Movie with ID {movie_id} not found")

            # Increment the watch count
            cursor.execute("UPDATE movies SET watch_count = watch_count + 1 WHERE id = ?", (movie_id,))
            conn.commit()

            logger.info("Watch count incremented for movie with ID: %d", movie_id)

    except sqlite3.Error as e:
        logger.error("Database error while updating watch count for movie with ID %d: %s", movie_id, str(e))
        raise e