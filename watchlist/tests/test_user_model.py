import pytest

from movie_collection.models.user_model import Users


@pytest.fixture
def sample_user():
    return {
        "username": "testuser",
        "password": "securepassword123"
    }


##########################################################
# User Creation
##########################################################

def test_create_user(session, sample_user):
    """Test creating a new user with a unique username."""
    Users.create_user(**sample_user)
    user = session.query(Users).filter_by(username=sample_user["username"]).first()
    assert user is not None, "User should be created in the database."
    assert user.username == sample_user["username"], "Username should match the input."
    assert len(user.salt) == 32, "Salt should be 32 characters (hex)."
    assert len(user.password) == 64, "Password should be a 64-character SHA-256 hash."

def test_create_duplicate_user(session, sample_user):
    """Test attempting to create a user with a duplicate username."""
    # Clear existing data
    session.query(Users).delete()
    session.commit()

    Users.create_user(**sample_user)

    with pytest.raises(ValueError, match="User with username 'testuser' already exists"):
        Users.create_user(**sample_user)


##########################################################
# User Authentication
##########################################################

def test_check_password_correct(session, sample_user):
    """Test checking the correct password."""
    # Clear existing data
    session.query(Users).delete()
    session.commit()
    
    Users.create_user(**sample_user)
    assert Users.check_password(sample_user["username"], sample_user["password"]) is True, "Password should match."

def test_check_password_incorrect(session, sample_user):
    """Test checking an incorrect password."""
    # Clear existing data
    session.query(Users).delete()
    session.commit()

    Users.create_user(**sample_user)
    assert Users.check_password(sample_user["username"], "wrongpassword") is False, "Password should not match."

def test_check_password_user_not_found(session):
    """Test checking password for a non-existent user."""
    # Clear existing data
    session.query(Users).delete()
    session.commit()
    
    with pytest.raises(ValueError, match="User nonexistentuser not found"):
        Users.check_password("nonexistentuser", "password")

##########################################################
# Update Password
##########################################################

def test_update_password(session, sample_user):
    """Test updating the password for an existing user."""
    Users.create_user(**sample_user)
    new_password = "newpassword456"
    Users.update_password(sample_user["username"], new_password)
    assert Users.check_password(sample_user["username"], new_password) is True, "Password should be updated successfully."

def test_update_password_user_not_found(session):
    """Test updating the password for a non-existent user."""
    with pytest.raises(ValueError, match="User nonexistentuser not found"):
        Users.update_password("nonexistentuser", "newpassword")