import pytest

from watchlist.movie_collection.models.watchlist_model import WatchlistModel
from watchlist.movie_collection.models.movie_model import Movie


@pytest.fixture()
def watchlist_model():
    """Fixture to provide a new instance of WatchlistModel for each test."""
    return WatchlistModel()

@pytest.fixture
def mock_update_watch_count(mocker):
    """Mock the update_watch_count function for testing purposes."""
    return mocker.patch("movie_collection.models.watchlist_model.update_watch_count")

"""Fixtures providing sample movies for the tests."""
@pytest.fixture
def sample_movie1():
    return Movie(1, 'Director 1', 'Movie 1', 2022, 'Horror', 180, 1.2)

@pytest.fixture
def sample_movie2():
    return Movie(2, 'Director 2', 'Movie 2', 2021, 'Sci-Fi', 155, 9.9)

@pytest.fixture
def sample_watchlist(sample_movie1, sample_movie2):
    return [sample_movie1, sample_movie2]


##################################################
# Add Movie Management Test Cases
##################################################

def test_add_movie_to_watchlist(watchlist_model, sample_movie1):
    """Test adding a movie to the watchlist."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    assert len(watchlist_model.watchlist) == 1
    assert watchlist_model.watchlist[0].title == 'Movie 1'

def test_add_duplicate_movie_to_watchlist(watchlist_model, sample_movie1):
    """Test error when adding a duplicate movie to the watchlist by ID."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    with pytest.raises(ValueError, match="Movie with ID 1 already exists in the watchlist"):
        watchlist_model.add_movie_to_watchlist(sample_movie1)

##################################################
# Remove Movie Management Test Cases
##################################################

def test_remove_movie_from_watchlist_by_movie_id(watchlist_model, sample_watchlist):
    """Test removing a movie from the watchlist by movie_id."""
    watchlist_model.watchlist.extend(sample_watchlist)
    assert len(watchlist_model.watchlist) == 2

    watchlist_model.remove_movie_by_movie_id(1)
    assert len(watchlist_model.watchlist) == 1, f"Expected 1 movie, but got {len(watchlist_model.watchlist)}"
    assert watchlist_model.watchlist[0].id == 2, "Expected movie with id 2 to remain"

def test_remove_movie_by_film_number(watchlist_model, sample_watchlist):
    """Test removing a movie from the watchlist by film number."""
    watchlist_model.watchlist.extend(sample_watchlist)
    assert len(watchlist_model.watchlist) == 2

    # Remove movie at film number 1 (first movie)
    watchlist_model.remove_movie_by_film_number(1)
    assert len(watchlist_model.watchlist) == 1, f"Expected 1 movie, but got {len(watchlist_model.watchlist)}"
    assert watchlist_model.watchlist[0].id == 2, "Expected movie with id 2 to remain"

def test_clear_watchlist(watchlist_model, sample_movie1):
    """Test clearing the entire watchlist."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    watchlist_model.clear_watchlist()
    assert len(watchlist_model.watchlist) == 0, "Watchlist should be empty after clearing"

def test_clear_watchlist_empty_watchlist(watchlist_model, caplog):
    """Test clearing the entire watchlist when it's empty."""
    watchlist_model.clear_watchlist()
    assert len(watchlist_model.watchlist) == 0, "Watchlist should be empty after clearing"
    assert "Clearing an empty watchlist" in caplog.text, "Expected warning message when clearing an empty watchlist"

##################################################
# Filmlisting Management Test Cases
##################################################

def test_move_movie_to_film_number(watchlist_model, sample_watchlist):
    """Test moving a movie to a specific film number in the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.move_movie_to_film_number(2, 1)  # Move Movie 2 to the first position
    assert watchlist_model.watchlist[0].id == 2, "Expected Movie 2 to be in the first position"
    assert watchlist_model.watchlist[1].id == 1, "Expected Movie 1 to be in the second position"

def test_move_movie_invalid_film_number(watchlist_model, sample_movie1):
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    with pytest.raises(ValueError, match="Invalid film number: 0"):
        watchlist_model.move_movie_to_film_number(1, 0)  # Invalid film number
    with pytest.raises(ValueError, match="Invalid film number: 2"):
        watchlist_model.move_movie_to_film_number(1, 2)  # Out of range

def test_swap_movies_in_watchlist(watchlist_model, sample_watchlist):
    """Test swapping the positions of two movies in the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.swap_movies_in_watchlist(1, 2)  # Swap positions of Movie 1 and Movie 2
    assert watchlist_model.watchlist[0].id == 2, "Expected Movie 2 to be in the first position"
    assert watchlist_model.watchlist[1].id == 1, "Expected Movie 1 to be in the second position"

def test_swap_movie_with_itself(watchlist_model, sample_movie1):
    """Test swapping the position of a movie with itself raises an error."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    with pytest.raises(ValueError, match="Cannot swap a movie with itself"):
        watchlist_model.swap_movies_in_watchlist(1, 1)  # Swap positions of Movie 1 with itself

def test_move_movie_to_end(watchlist_model, sample_watchlist):
    """Test moving a movie to the end of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.move_movie_to_end(1)  # Move Movie 1 to the end
    assert watchlist_model.watchlist[1].id == 1, "Expected Movie 1 to be at the end"

def test_move_movie_to_beginning(watchlist_model, sample_watchlist):
    """Test moving a movie to the beginning of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.move_movie_to_beginning(2)  # Move Movie 2 to the beginning
    assert watchlist_model.watchlist[0].id == 2, "Expected Movie 2 to be at the beginning"

##################################################
# Movie Retrieval Test Cases
##################################################

def test_get_movie_by_film_number(watchlist_model, sample_watchlist):
    """Test successfully retrieving a movie from the watchlist by film number."""
    watchlist_model.watchlist.extend(sample_watchlist)

    retrieved_movie = watchlist_model.get_movie_by_film_number(1)
    assert retrieved_movie.id == 1
    assert retrieved_movie.title == 'Movie 1'
    assert retrieved_movie.director == 'Director 1'
    assert retrieved_movie.year == 2022
    assert retrieved_movie.duration == 180
    assert retrieved_movie.genre == 'Horror'
    assert retrieved_movie.rating == 1.2

def test_get_all_movies(watchlist_model, sample_watchlist):
    """Test successfully retrieving all movies from the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    all_movies = watchlist_model.get_all_movies()
    assert len(all_movies) == 2
    assert all_movies[0].id == 1
    assert all_movies[1].id == 2

def test_get_movie_by_movie_id(watchlist_model, sample_movie1):
    """Test successfully retrieving a movie from the watchlist by movie ID."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    retrieved_movie = watchlist_model.get_movie_by_movie_id(1)

    assert retrieved_movie.id == 1
    assert retrieved_movie.title == 'Movie 1'
    assert retrieved_movie.director == 'Director 1'
    assert retrieved_movie.year == 2022
    assert retrieved_movie.duration == 180
    assert retrieved_movie.genre == 'Horror'
    assert retrieved_movie.rating == 1.2

def test_get_current_movie(watchlist_model, sample_watchlist):
    """Test successfully retrieving the current movie from the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    current_movie = watchlist_model.get_current_movie()
    assert current_movie.id == 1
    assert current_movie.title == 'Movie 1'
    assert current_movie.director == 'Director 1'
    assert current_movie.year == 2022
    assert current_movie.duration == 180
    assert current_movie.genre == 'Horror'
    assert current_movie.rating == 1.2

def test_get_watchlist_length(watchlist_model, sample_watchlist):
    """Test getting the length of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)
    assert watchlist_model.get_watchlist_length() == 2, "Expected watchlist length to be 2"

def test_get_watchlist_duration(watchlist_model, sample_watchlist):
    """Test getting the total duration of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)
    assert watchlist_model.get_watchlist_duration() == 335, "Expected watchlist duration to be 335 minutes"

##################################################
# Utility Function Test Cases
##################################################

def test_check_if_empty_non_empty_watchlist(watchlist_model, sample_movie1):
    """Test check_if_empty does not raise error if watchlist is not empty."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    try:
        watchlist_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty watchlist")

def test_check_if_empty_empty_watchlist(watchlist_model):
    """Test check_if_empty raises error when watchlist is empty."""
    watchlist_model.clear_watchlist()
    with pytest.raises(ValueError, match="Watchlist is empty"):
        watchlist_model.check_if_empty()

def test_validate_movie_id(watchlist_model, sample_movie1):
    """Test validate_movie_id does not raise error for valid movie ID."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    try:
        watchlist_model.validate_movie_id(1)
    except ValueError:
        pytest.fail("validate_movie_id raised ValueError unexpectedly for valid movie ID")

def test_validate_movie_id_no_check_in_watchlist(watchlist_model):
    """Test validate_movie_id does not raise error for valid movie ID when the id isn't in the watchlist."""
    try:
        watchlist_model.validate_movie_id(1, check_in_watchlist=False)
    except ValueError:
        pytest.fail("validate_movie_id raised ValueError unexpectedly for valid movie ID")

def test_validate_movie_id_invalid_id(watchlist_model):
    """Test validate_movie_id raises error for invalid movie ID."""
    with pytest.raises(ValueError, match="Invalid movie id: -1"):
        watchlist_model.validate_movie_id(-1)

    with pytest.raises(ValueError, match="Invalid movie id: invalid"):
        watchlist_model.validate_movie_id("invalid")

def test_validate_film_number(watchlist_model, sample_movie1):
    """Test validate_film_number does not raise error for valid film number."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)
    try:
        watchlist_model.validate_film_number(1)
    except ValueError:
        pytest.fail("validate_film_number raised ValueError unexpectedly for valid film number")

def test_validate_film_number_invalid(watchlist_model, sample_movie1):
    """Test validate_film_number raises error for invalid film number."""
    watchlist_model.add_movie_to_watchlist(sample_movie1)

    with pytest.raises(ValueError, match="Invalid film number: 0"):
        watchlist_model.validate_film_number(0)

    with pytest.raises(ValueError, match="Invalid film number: 2"):
        watchlist_model.validate_film_number(2)

    with pytest.raises(ValueError, match="Invalid film number: invalid"):
        watchlist_model.validate_film_number("invalid")

##################################################
# Watchback Test Cases
##################################################

def test_play_current_movie(watchlist_model, sample_watchlist, mock_update_watch_count):
    """Test playing the current movie."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.play_current_movie()

    # Assert that CURRENT_FILM_NUMBER has been updated to 2
    assert watchlist_model.current_film_number == 2, f"Expected film number to be 2, but got {watchlist_model.current_film_number}"

    # Assert that update_watch_count was called with the id of the first movie
    mock_update_watch_count.assert_called_once_with(1)

    # Get the second movie from the iterator (which will increment CURRENT_FILM_NUMBER back to 1)
    watchlist_model.play_current_movie()

    # Assert that CURRENT_FILM_NUMBER has been updated back to 1
    assert watchlist_model.current_film_number == 1, f"Expected film number to be 1, but got {watchlist_model.current_film_number}"

    # Assert that update_watch_count was called with the id of the second movie
    mock_update_watch_count.assert_called_with(2)

def test_rewind_watchlist(watchlist_model, sample_watchlist):
    """Test rewinding the iterator to the beginning of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)
    watchlist_model.current_film_number = 2

    watchlist_model.rewind_watchlist()
    assert watchlist_model.current_film_number == 1, "Expected to rewind to the first film"

def test_go_to_film_number(watchlist_model, sample_watchlist):
    """Test moving the iterator to a specific film number in the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.go_to_film_number(2)
    assert watchlist_model.current_film_number == 2, "Expected to be at film 2 after moving movie"

def test_play_entire_watchlist(watchlist_model, sample_watchlist, mock_update_watch_count):
    """Test playing the entire watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)

    watchlist_model.play_entire_watchlist()

    # Check that all watch counts were updated
    mock_update_watch_count.assert_any_call(1)
    mock_update_watch_count.assert_any_call(2)
    assert mock_update_watch_count.call_count == len(watchlist_model.watchlist)

    # Check that the current film number was updated back to the first movie
    assert watchlist_model.current_film_number == 1, "Expected to loop back to the beginning of the watchlist"

def test_play_rest_of_watchlist(watchlist_model, sample_watchlist, mock_update_watch_count):
    """Test playing from the current position to the end of the watchlist."""
    watchlist_model.watchlist.extend(sample_watchlist)
    watchlist_model.current_film_number = 2

    watchlist_model.play_rest_of_watchlist()

    # Check that watch counts were updated for the remaining movies
    mock_update_watch_count.assert_any_call(2)
    assert mock_update_watch_count.call_count == 1

    assert watchlist_model.current_track_number == 1, "Expected to loop back to the beginning of the watchlist"