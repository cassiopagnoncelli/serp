import pytest
from app.models.user import User
from lib.core.record.uuid import generate_id
from lib.core.authentication.passwords import verify_password

@pytest.mark.unit
def test_create_user(db_session):
    password = "secret"
    user = User(
        email="test@example.com",
        password=password,
        name="Test User",
        account_uuid=generate_id("acc")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.id is not None
    assert user.uuid.startswith("usr_")
    assert user.email == "test@example.com"
    assert verify_password(password, user.enc_password)
    assert user.name == "Test User"
    assert user.account_uuid.startswith("acc_")

@pytest.mark.unit
def test_uuid_is_unique(db_session):
    user1 = User(
        email="a@example.com",
        password="pw1",
        name="A",
        account_uuid=generate_id("acc")
    )
    user2 = User(
        email="b@example.com",
        password="pw2",
        name="B",
        account_uuid=generate_id("acc")
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    assert user1.uuid != user2.uuid

@pytest.mark.unit
def test_email_unique_constraint(db_session):
    user1 = User(
        email="unique@example.com",
        password="pw",
        name="U",
        account_uuid=generate_id("acc")
    )
    db_session.add(user1)
    db_session.commit()
    user2 = User(
        email="unique@example.com",
        password="pw2",
        name="U2",
        account_uuid=generate_id("acc")
    )
    db_session.add(user2)
    with pytest.raises(Exception):
        db_session.commit()
