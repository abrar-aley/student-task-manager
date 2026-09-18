import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.course import Course


@pytest.fixture
def app():
    application = create_app("app.config.TestConfig")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Creates a user directly in the DB (not via signup route) for tests that need one to already exist."""
    with app.app_context():
        user = User(email="student@example.com")
        user.set_password("password123")
        _db.session.add(user)
        _db.session.commit()
        _db.session.refresh(user)
        return user.id, user.email


@pytest.fixture
def auth_client(client, test_user):
    """A test client that's already logged in as test_user."""
    user_id, email = test_user
    client.post("/login", data={"email": email, "password": "password123"})
    return client


@pytest.fixture
def test_course(app, test_user):
    """A course belonging to test_user."""
    user_id, _ = test_user
    with app.app_context():
        course = Course(user_id=user_id, name="Object Oriented Programming", code="CSC-241")
        _db.session.add(course)
        _db.session.commit()
        _db.session.refresh(course)
        return course.id