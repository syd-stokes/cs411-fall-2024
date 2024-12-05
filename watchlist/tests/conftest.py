import pytest
from config import TestConfig
from app import create_app
from movie_collection.db import db


@pytest.fixture(scope='module')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(app):
    """Provide a database session for tests."""
    with app.app_context():
        yield db.session
