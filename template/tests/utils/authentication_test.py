import pytest
from datetime import datetime, timedelta
from app.utils.authentication import (
    authenticate_user,
    generate_user_token,
    decode_user_token,
    login_user_with_password,
    find_user_by_email,
    persist_user_token
)
from app.models import User, Token
from lib.core.authentication.passwords import hash_password
from lib.core.record.uuid import generate_id

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        enc_password=hash_password("testpassword"),
        name="Test User",
        status="active",
        login_provider="email",
        account_uuid=generate_id("acc")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_find_user_by_email(db_session, test_user):
    # Test finding existing user
    found_user = find_user_by_email("test@example.com", db_session)
    assert found_user is not None
    assert found_user.email == test_user.email
    
    # Test finding non-existent user
    not_found_user = find_user_by_email("nonexistent@example.com", db_session)
    assert not_found_user is None

def test_authenticate_user(db_session, test_user):
    # Test successful authentication
    authenticated_user = authenticate_user("test@example.com", "testpassword", db_session)
    assert authenticated_user is not None
    assert authenticated_user.email == test_user.email
    
    # Test wrong password
    wrong_password_user = authenticate_user("test@example.com", "wrongpassword", db_session)
    assert wrong_password_user is None
    
    # Test non-existent user
    nonexistent_user = authenticate_user("nonexistent@example.com", "testpassword", db_session)
    assert nonexistent_user is None

def test_generate_and_decode_user_token(test_user):
    # Test token generation
    user_data = test_user.model_dump()
    token = generate_user_token(user_data)
    assert token is not None
    
    # Test token decoding
    decoded_data = decode_user_token(token)
    assert decoded_data is not None
    assert decoded_data["email"] == test_user.email
    assert decoded_data["id"] == test_user.id
    
    # Test invalid token
    invalid_token = "invalid.token.here"
    decoded_invalid = decode_user_token(invalid_token)
    assert decoded_invalid is None

def test_persist_user_token(db_session, test_user):
    token = "test.token.here"
    expires_minutes = 30
    ip_address = "127.0.0.1"
    user_agent = "test-agent"
    location = "test-location"
    device = "test-device"
    
    persisted_token = persist_user_token(
        test_user.id,
        token,
        expires_minutes,
        ip_address,
        user_agent,
        location,
        device,
        db_session
    )
    
    assert persisted_token is not None
    assert persisted_token.user_id == test_user.id
    assert persisted_token.token == token
    assert persisted_token.ip_address == ip_address
    assert persisted_token.user_agent == user_agent
    assert persisted_token.location == location
    assert persisted_token.device == device
    
    # Verify token was saved in database
    saved_token = db_session.get(Token, persisted_token.id)
    assert saved_token is not None
    assert saved_token.token == token

def test_login_user_with_password(db_session, test_user):
    # Test successful login
    token = login_user_with_password(
        "test@example.com",
        "testpassword",
        ip_address="127.0.0.1",
        user_agent="test-agent",
        session=db_session
    )
    assert token is not None
    
    # Verify token was persisted
    saved_token = db_session.query(Token).filter(Token.user_id == test_user.id).first()
    assert saved_token is not None
    assert saved_token.token == token
    
    # Test login with wrong password
    wrong_password_token = login_user_with_password(
        "test@example.com",
        "wrongpassword",
        session=db_session
    )
    assert wrong_password_token is None
    
    # Test login with non-existent user
    nonexistent_token = login_user_with_password(
        "nonexistent@example.com",
        "testpassword",
        session=db_session
    )
    assert nonexistent_token is None

