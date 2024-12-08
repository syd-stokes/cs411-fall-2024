import pytest
from unittest.mock import patch
from movie_collection.models.tmdb_api_model import TMDbAPI


@pytest.fixture
def tmdb_api():
    """Fixture to provide a new instance of TMDbAPI for each test."""
    return TMDbAPI(api_key="dummy_api_key")


@pytest.fixture
def mock_tmdb_request(mocker):
    """Mock the _make_request method in TMDbAPI."""
    return mocker.patch("movie_collection.models.tmdb_api_model.TMDbAPI._make_request")



def test_get_movies_by_director_success(tmdb_api, mock_tmdb_request):
    mock_response = {
        "results": [
            {
                "name": "Christopher Nolan",
                "known_for": [
                    {
                        "media_type": "movie",
                        "title": "Inception",
                        "release_date": "2010-07-16",
                        "vote_average": 8.8,
                        "overview": "A mind-bending thriller."
                    }
                ]
            }
        ]
    }
    mock_tmdb_request.return_value = mock_response

    movies = tmdb_api.get_movies_by_director("Christopher Nolan")
    assert len(movies) == 1
    assert movies[0]["title"] == "Inception"
    assert movies[0]["rating"] == 8.8
    assert "mind-bending" in movies[0]["overview"]


def test_get_top_rated_movies_success(tmdb_api, mock_tmdb_request):
    mock_response = {
        "results": [
            {
                "title": "The Shawshank Redemption",
                "release_date": "1994-09-22",
                "vote_average": 9.3,
                "overview": "Two imprisoned men bond over a number of years."
            },
            {
                "title": "The Godfather",
                "release_date": "1972-03-24",
                "vote_average": 9.2,
                "overview": "The aging patriarch of an organized crime dynasty transfers control."
            }
        ]
    }
    mock_tmdb_request.return_value = mock_response

    movies = tmdb_api.get_top_rated_movies()
    assert len(movies) == 2
    assert movies[0]["title"] == "The Shawshank Redemption"
    assert movies[1]["title"] == "The Godfather"

def test_get_movies_by_director_failure(tmdb_api, mock_tmdb_request):
    mock_response = {
        "status_code": 404,
        "status_message": "The resource you requested could not be found."
    }
    mock_tmdb_request.return_value = mock_response

    movies = tmdb_api.get_movies_by_director("Christopher Nolan")
    assert len(movies) == 0

def test_get_top_rated_movies_failure(tmdb_api, mock_tmdb_request):
    mock_response = {
        "status_code": 404,
        "status_message": "The resource you requested could not be found."
    }
    mock_tmdb_request.return_value = mock_response

    movies = tmdb_api.get_top_rated_movies()
    assert len(movies) == 0


def test_get_movies_by_director_no_results(tmdb_api, mock_tmdb_request):
    mock_response = {
        "results": []
    }
    mock_tmdb_request.return_value = mock_response

    movies = tmdb_api.get_movies_by_director("Christopher Nolan")
    assert len(movies) == 0

def test_get_top_rated_movies_no_results(tmdb_api, mock_tmdb_request):
    mock_response = {
        "results": []
    }
    mock_tmdb_request.return_value = mock_response

    movies = tmdb_api.get_top_rated_movies()
    assert len(movies) == 0

