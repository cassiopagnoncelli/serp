import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from app.models.user import User

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.mark.unit
def test_create_user(session):
    user = User(email="test@example.com", password="secret", name="Test User")
    session.add(user)
    session.commit()
    session.refresh(user)
    assert user.id is not None
    assert user.uuid.startswith("usr_")
    assert user.email == "test@example.com"
    assert user.password == "secret"
    assert user.name == "Test User"

@pytest.mark.unit
def test_uuid_is_unique(session):
    user1 = User(email="a@example.com", password="pw1", name="A")
    user2 = User(email="b@example.com", password="pw2", name="B")
    session.add(user1)
    session.add(user2)
    session.commit()
    assert user1.uuid != user2.uuid

@pytest.mark.unit
def test_email_unique_constraint(session):
    user1 = User(email="unique@example.com", password="pw", name="U")
    session.add(user1)
    session.commit()
    user2 = User(email="unique@example.com", password="pw2", name="U2")
    session.add(user2)
    with pytest.raises(Exception):
        session.commit()
