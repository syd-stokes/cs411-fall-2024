import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_play_count(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("music_collection.models.playlist_model.update_play_count")

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_song1():
    return Song(1, 'Artist 1', 'Song 1', 2022, 'Pop', 180)

@pytest.fixture
def sample_song2():
    return Song(2, 'Artist 2', 'Song 2', 2021, 'Rock', 155)

@pytest.fixture
def sample_playlist(sample_song1, sample_song2):
    return [sample_song1, sample_song2]