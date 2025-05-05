import pytest
from app.models.user import User

@pytest.mark.unit
def test_create_user(db_session):
    user = User(email="test@example.com", password="secret", name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.id is not None
    assert user.uuid.startswith("usr_")
    assert user.email == "test@example.com"
    assert user.password == "secret"
    assert user.name == "Test User"

@pytest.mark.unit
def test_uuid_is_unique(db_session):
    user1 = User(email="a@example.com", password="pw1", name="A")
    user2 = User(email="b@example.com", password="pw2", name="B")
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    assert user1.uuid != user2.uuid

@pytest.mark.unit
def test_email_unique_constraint(db_session):
    user1 = User(email="unique@example.com", password="pw", name="U")
    db_session.add(user1)
    db_session.commit()
    user2 = User(email="unique@example.com", password="pw2", name="U2")
    db_session.add(user2)
    with pytest.raises(Exception):
        db_session.commit()
