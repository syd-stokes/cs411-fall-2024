from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
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

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the table."""

    # Call the function to create a new meal
    create_meal(meal="Pasta", cuisine="Italian", price=20.00, difficulty="LOW")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Pasta", "Italian", 20.00, "LOW")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meal.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Pasta'"):
        create_meal(meal="Pasta", cuisine="Italian", price=25.00, difficulty="MED")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (e.g., negative price)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -10. Price must be a positive number"):
        create_meal("Test Meal", "Italian", -10, "MED")

    # Attempt to create a meal with a non-integer price
    with pytest.raises(ValueError, match="Invalid price: INVALID. Price must be a positive number"):
        create_meal("Test Meal", "Italian", "INVALID", "MED")



def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (e.g., neither 'LOW', 'MED', or 'HIGH')."""

    # Attempt to create a meal with a difficulty not set to Low medium or high.  
    with pytest.raises(ValueError, match="Invalid difficulty level: EASY. Must be 'LOW', 'MED', or 'HIGH'"):
        create_meal("Test Meal", "Italian", 10, "EASY")


def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the table by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

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

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)
    

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meal table (removes all meal)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()


######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 20.00, "LOW", False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Pasta", "Italian", 20.00, "LOW")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_leaderboard(mock_cursor):
    """Test retrieving leaderboard sorted by total wins."""

    # Mock database response
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Italian", 10.00, "LOW", 10, 8, 0.8),
        (2, "Meal B", "Mexican", 12.00, "MED", 5, 3, 0.6),
        (3, "Meal C", "Japanese", 15.00, "HIGH", 8, 4, 0.5),
    ]

    # Call get_leaderboard with sort_by="wins"
    leaderboard = get_leaderboard(sort_by="wins")

    # Expected result for sorting by wins
    expected_result = [
        {"id": 1, "meal": "Meal A", "cuisine": "Italian", "price": 10.00, "difficulty": "LOW", "battles": 10, "wins": 8, "win_pct": 80.0},
        {"id": 2, "meal": "Meal B", "cuisine": "Mexican", "price": 12.00, "difficulty": "MED", "battles": 5, "wins": 3, "win_pct": 60.0},
        {"id": 3, "meal": "Meal C", "cuisine": "Japanese", "price": 15.00, "difficulty": "HIGH", "battles": 8, "wins": 4, "win_pct": 50.0},
    ]

    # Assertion to check if leaderboard matches expected result
    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    # Ensure SQL query is correct
    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0 ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "SQL query did not match expected structure"



def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal by name."""

    # Mock the database response for an existing meal
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 20.00, "LOW", False)

    # Call the function and check the result
    result = get_meal_by_name("Pasta")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(id=1, meal="Pasta", cuisine="Italian", price=20.00, difficulty="LOW")

    # Assert that the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query matches the expected structure
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Pasta",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_meal_by_name_deleted_meal(mock_cursor):
    """Test retrieving a meal that has been marked as deleted."""

    # Mock the database response for a deleted meal
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 20.00, "LOW", True)

    # Check that ValueError is raised with the correct message
    with pytest.raises(ValueError, match="Meal with name Pasta has been deleted"):
        get_meal_by_name("Pasta")

def test_get_meal_by_name_not_found(mock_cursor):
    """Test retrieving a meal that does not exist in the database."""

    # Simulate a meal not found in the database
    mock_cursor.fetchone.return_value = None

    # Check that ValueError is raised with the correct message
    with pytest.raises(ValueError, match="Meal with name Pasta not found"):
        get_meal_by_name("Pasta")

def test_update_meal_stats_win(mock_cursor):
    """Test updating meal statistics with a win result."""
    # Simulate the meal exists and is not deleted
    mock_cursor.fetchone.return_value = (False,)

    # Call the function with a win result
    update_meal_stats(1, "win")

    # Ensure the correct update query was executed
    expected_query = "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?"
    actual_query = mock_cursor.execute.call_args[0][0]
    assert actual_query == expected_query, "SQL query for 'win' result did not match expected structure."

    # Ensure the correct meal_id was used in the query
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"Expected arguments {expected_arguments}, got {actual_arguments}"

def test_update_meal_stats_loss(mock_cursor):
    """Test updating meal statistics with a loss result."""
    # Simulate the meal exists and is not deleted
    mock_cursor.fetchone.return_value = (False,)

    # Call the function with a loss result
    update_meal_stats(1, "loss")

    # Ensure the correct update query was executed
    expected_query = "UPDATE meals SET battles = battles + 1 WHERE id = ?"
    actual_query = mock_cursor.execute.call_args[0][0]
    assert actual_query == expected_query, "SQL query for 'loss' result did not match expected structure."

    # Ensure the correct meal_id was used in the query
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"Expected arguments {expected_arguments}, got {actual_arguments}"

def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test updating statistics for a meal that has been marked as deleted."""
    # Simulate that the meal is marked as deleted
    mock_cursor.fetchone.return_value = (True,)

    # Check that ValueError is raised with the correct message
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

def test_update_meal_stats_meal_not_found(mock_cursor):
    """Test updating statistics for a meal that does not exist in the database."""
    # Simulate that the meal is not found (fetchone returns None)
    mock_cursor.fetchone.return_value = None

    # Check that ValueError is raised with the correct message
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        update_meal_stats(1, "win")

def test_update_meal_stats_invalid_result(mock_cursor):
    """Test updating meal statistics with an invalid result."""
    # Simulate the meal exists and is not deleted
    mock_cursor.fetchone.return_value = (False,)

    # Check that ValueError is raised with the correct message
    with pytest.raises(ValueError, match="Invalid result: tie. Expected 'win' or 'loss'."):
        update_meal_stats(1, "tie")
