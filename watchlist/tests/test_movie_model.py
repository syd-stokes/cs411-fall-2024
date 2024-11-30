from contextlib import contextmanager
import re
import sqlite3

import pytest

from movie_collection.models.movie_model import (
    Movie,
    create_movie,
    clear_catalog,
    delete_movie,
    get_movie_by_id,
    get_movie_by_compound_key,
    get_all_movies,
    get_random_movie,
    update_watch_count
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None
    
    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("movie_collection.models.movie_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_movie(mock_cursor):
    """Test creating a new movie in the catalog."""

    # Call the function to create a new movie
    create_movie(director="Director Name", title="Movie Title", year=2022, genre="Horror", duration=180, rating=8.6)

    expected_query = normalize_whitespace("""
        INSERT INTO movies (director, title, year, genre, duration, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Director Name", "Movie Title", 2022, "Horror", 180, 8.6)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_movie_duplicate(mock_cursor):
    """Test creating a movie with a duplicate director, title, and year (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: movies.director, movies.title, movies.year")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Movie with director 'Director Name', title 'Movie Title', and year 2022 already exists."):
        create_movie(director="Director Name", title="Movie Title", year=2022, genre="Horror", duration=180, rating=8.6)

def test_create_movie_invalid_duration():
    """Test error when trying to create a movie with an invalid duration (e.g., negative duration)"""

    # Attempt to create a movie with a negative duration
    with pytest.raises(ValueError, match="Invalid movie duration: -180 \(must be a positive integer\)."):
        create_movie(director="Director Name", title="Movie Title", year=2022, genre="Horror", duration=-180, rating=8.6)

    # Attempt to create a movie with a non-integer duration
    with pytest.raises(ValueError, match="Invalid movie duration: invalid \(must be a positive integer\)."):
        create_movie(director="Director Name", title="Movie Title", year=2022, genre="Horror", duration="invalid", rating=8.6)

def test_create_movie_invalid_year():
    """Test error when trying to create a movie with an invalid year (e.g. non-integer)."""

    # Attempt to create a movie with a year less than 0
    with pytest.raises(ValueError, match="Invalid year provided: -1899 \(must be a positive integer\)."):
        create_movie(director="Director Name", title="Movie Title", year=-1899, genre="Horror", duration=180, rating=8.6)

    # Attempt to create a movie with a non-integer year
    with pytest.raises(ValueError, match="Invalid year provided: invalid \(must be a positive integer\)."):
        create_movie(director="Director Name", title="Movie Title", year="invalid", genre="Horror", duration=180, rating=8.6)

def test_delete_movie(mock_cursor):
    """Test soft deleting a movie from the catalog by movie ID."""

    # Simulate that the movie exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_movie function
    delete_movie(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM movies WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE movies SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_movie_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent movie."""

    # Simulate that no movie exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent movie
    with pytest.raises(ValueError, match="Movie with ID 999 not found"):
        delete_movie(999)

def test_delete_movie_already_deleted(mock_cursor):
    """Test error when trying to delete a movie that's already marked as deleted."""

    # Simulate that the movie exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a movie that's already been deleted
    with pytest.raises(ValueError, match="Movie with ID 999 has already been deleted"):
        delete_movie(999)

def test_clear_catalog(mock_cursor, mocker):
    """Test clearing the entire movie catalog (removes all movies)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_movie_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_catalog()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_movie_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


######################################################
#
#    Get Movie
#
######################################################

def test_get_movie_by_id(mock_cursor):
    # Simulate that the movie exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Director Name", "Movie Title", 2022, "Horror", 180, 8.6, False)

    # Call the function and check the result
    result = get_movie_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Movie(1, "Director Name", "Movie Title", 2022, "Horror", 180, 8.6)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, director, title, year, genre, duration, rating, deleted FROM movies WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_movie_by_id_bad_id(mock_cursor):
    # Simulate that no movie exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the movie is not found
    with pytest.raises(ValueError, match="Movie with ID 999 not found"):
        get_movie_by_id(999)

def test_get_movie_by_compound_key(mock_cursor):
    # Simulate that the movie exists (director = "Director Name", title = "Movie Title", year = 2022, duration = 180, rating = 8.6)
    mock_cursor.fetchone.return_value = (1, "Director Name", "Movie Title", 2022, "Horror", 180, 8.6, False)

    # Call the function and check the result
    result = get_movie_by_compound_key("Director Name", "Movie Title", 2022)

    # Expected result based on the simulated fetchone return value
    expected_result = Movie(1, "Director Name", "Movie Title", 2022, "Horror", 180, 8.6)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, director, title, year, genre, duration, rating, deleted FROM movies WHERE director = ? AND title = ? AND year = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Director Name", "Movie Title", 2022)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_all_movies(mock_cursor):
    """Test retrieving all movies that are not marked as deleted."""

    # Simulate that there are multiple movies in the database
    mock_cursor.fetchall.return_value = [
        (1, "Director A", "Movie A", 2020, "Comedy", 210, 4.3, 10, False),
        (2, "Director B", "Movie B", 2021, "Action", 180, 9.2, 20, False),
        (3, "Director C", "Movie C", 2022, "Thriller", 200, 7.5, 5, False)
    ]

    # Call the get_all_movies function
    movies = get_all_movies()

    # Ensure the results match the expected output
    expected_result = [
        {"id": 1, "director": "Director A", "title": "Movie A", "year": 2020, "genre": "Comedy", "duration": 210, "rating" : 4.3, "watch_count": 10},
        {"id": 2, "director": "Director B", "title": "Movie B", "year": 2021, "genre": "Action", "duration": 180, "rating" : 9.2, "watch_count": 20},
        {"id": 3, "director": "Director C", "title": "Movie C", "year": 2022, "genre": "Thriller", "duration": 200, "rating" : 7.5, "watch_count": 5}
    ]

    assert movies == expected_result, f"Expected {expected_result}, but got {movies}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, director, title, year, genre, duration, rating, watch_count
        FROM movies
        WHERE deleted = FALSE
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_movies_empty_catalog(mock_cursor, caplog):
    """Test that retrieving all movies returns an empty list when the catalog is empty and logs a warning."""

    # Simulate that the catalog is empty (no movies)
    mock_cursor.fetchall.return_value = []

    # Call the get_all_movies function
    result = get_all_movies()

    rows = mock_cursor.fetchall()

    # Ensure the result is an empty list
    assert result == [], f"Expected empty list, but got {result}"

    # Ensure that a warning was logged
    assert "The movie catalog is empty." in caplog.text, "Expected warning about empty catalog not found in logs."

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, director, title, year, genre, duration, rating, watch_count FROM movies WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_movies_ordered_by_watch_count(mock_cursor):
    """Test retrieving all movies ordered by watch count."""

    # Simulate that there are multiple movies in the database
    mock_cursor.fetchall.return_value = [
        (2, "Director B", "Movie B", 2021, "Comedy", 180, 4.3, 20),
        (1, "Director A", "Movie A", 2020, "Action", 210, 9.2, 10),
        (3, "Director C", "Movie C", 2022, "Thriller", 200, 7.5, 5)
    ]

    # Call the get_all_movies function with sort_by_watch_count = True
    movies = get_all_movies(sort_by_rating=False, sort_by_watch_count=True)

    # Ensure the results are sorted by watch count
    expected_result = [
        {"id": 2, "director": "Director B", "title": "Movie B", "year": 2021, "genre": "Comedy", "duration": 180, "rating" : 4.3, "watch_count": 20},
        {"id": 1, "director": "Director A", "title": "Movie A", "year": 2020, "genre": "Action", "duration": 210, "rating" : 9.2,  "watch_count": 10},
        {"id": 3, "director": "Director C", "title": "Movie C", "year": 2022, "genre": "Thriller", "duration": 200, "rating" : 7.5,  "watch_count": 5}
    ]

    assert movies == expected_result, f"Expected {expected_result}, but got {movies}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, director, title, year, genre, duration, rating, watch_count
        FROM movies
        WHERE deleted = FALSE
        ORDER BY watch_count DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_all_movies_ordered_by_rating(mock_cursor):
    """Test retrieving all movies ordered by rating."""

    # Simulate that there are multiple movies in the database
    mock_cursor.fetchall.return_value = [
        (1, "Director A", "Movie A", 2020, "Action", 210, 9.2, 10),
        (3, "Director C", "Movie C", 2022, "Thriller", 200, 7.5, 5),
        (2, "Director B", "Movie B", 2021, "Comedy", 180, 4.3, 20)
    ]

    # Call the get_all_movies function with sort_by_rating = True
    movies = get_all_movies(sort_by_rating=True, sort_by_watch_count=False)

    # Ensure the results are sorted by rating
    expected_result = [
        {"id": 1, "director": "Director A", "title": "Movie A", "year": 2020, "genre": "Action", "duration": 210, "rating" : 9.2,  "watch_count": 10},
        {"id": 3, "director": "Director C", "title": "Movie C", "year": 2022, "genre": "Thriller", "duration": 200, "rating" : 7.5,  "watch_count": 5},
        {"id": 2, "director": "Director B", "title": "Movie B", "year": 2021, "genre": "Comedy", "duration": 180, "rating" : 4.3, "watch_count": 20}
    ]

    assert movies == expected_result, f"Expected {expected_result}, but got {movies}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("""
        SELECT id, director, title, year, genre, duration, rating, watch_count
        FROM movies
        WHERE deleted = FALSE
        ORDER BY rating DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_random_movie(mock_cursor, mocker):
    """Test retrieving a random movie from the catalog."""

    # Simulate that there are multiple movies in the database
    mock_cursor.fetchall.return_value = [
        (1, "Director A", "Movie A", 2020, "Comedy", 210, 4.3, 10),
        (2, "Director B", "Movie B", 2021, "Action", 180, 7.5, 20),
        (3, "Director C", "Movie C", 2022, "Thriller", 200, 9.2, 5)
    ]

    # Mock random number generation to return the 2nd movie
    mock_random = mocker.patch("movie_collection.models.movie_model.get_random", return_value=2)

    # Call the get_random_movie method
    result = get_random_movie()

    # Expected result based on the mock random number and fetchall return value
    expected_result = Movie(2, "Director B", "Movie B", 2021, "Action", 180, 7.5)

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure that the random number was called with the correct number of movies
    mock_random.assert_called_once_with(3)

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, director, title, year, genre, duration, rating, watch_count FROM movies WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_get_random_movie_empty_catalog(mock_cursor, mocker):
    """Test retrieving a random movie when the catalog is empty."""

    # Simulate that the catalog is empty
    mock_cursor.fetchall.return_value = []

    # Expect a ValueError to be raised when calling get_random_movie with an empty catalog
    with pytest.raises(ValueError, match="The movie catalog is empty"):
        get_random_movie()

    # Ensure that the random number was not called since there are no movies
    mocker.patch("movie_collection.models.movie_model.get_random").assert_not_called()

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, director, title, year, genre, duration, rating, watch_count FROM movies WHERE deleted = FALSE")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

def test_update_watch_count(mock_cursor):
    """Test updating the watch count of a movie."""

    # Simulate that the movie exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_watch_count function with a sample movie ID
    movie_id = 1
    update_watch_count(movie_id)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE movies SET watch_count = watch_count + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (movie ID)
    expected_arguments = (movie_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

### Test for Updating a Deleted Movie:
def test_update_watch_count_deleted_movie(mock_cursor):
    """Test error when trying to update watch count for a deleted movie."""

    # Simulate that the movie exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted movie
    with pytest.raises(ValueError, match="Movie with ID 1 has been deleted"):
        update_watch_count(1)

    # Ensure that no SQL query for updating watch count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM movies WHERE id = ?", (1,))