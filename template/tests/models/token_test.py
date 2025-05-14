import pytest
from datetime import datetime, timedelta, UTC
from app.models.token import Token
from app.models.user import User
from lib.core.record.uuid import generate_id

def generate_unique_token():
    """Generate a unique token for testing"""
    return f"test_token_{generate_id('tkn')}"

def naive_to_utc(dt):
    """Convert a naive datetime to UTC timezone-aware datetime"""
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt

@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_token():
    # Create a user first
    user = await User.create(
        email="token_test@example.com",
        password="secret",
        name="Token Test User",
        account_uuid=generate_id("acc")
    )
    
    # Create a token
    token_value = generate_unique_token()
    expires_at = datetime.now(UTC) + timedelta(days=1)
    token = await Token.create(
        user=user,  # Using the relationship field
        token=token_value,
        expires_at=expires_at,
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0",
        location={"country": "US", "city": "New York"},
        device={"type": "mobile", "os": "iOS"}
    )
    
    # Verify token attributes
    assert token.user == user
    assert token.token == token_value
    assert naive_to_utc(token.expires_at) == expires_at
    assert token.ip_address == "127.0.0.1"
    assert token.user_agent == "Mozilla/5.0"
    assert token.location == {"country": "US", "city": "New York"}
    assert token.device == {"type": "mobile", "os": "iOS"}

@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_user_relationship():
    # Create a user
    user = await User.create(
        email="relationship_test@example.com",
        password="secret",
        name="Relationship Test User",
        account_uuid=generate_id("acc")
    )
    
    # Create multiple tokens for the user
    tokens = []
    for i in range(3):
        token = await Token.create(
            user=user,
            token=generate_unique_token(),
            expires_at=datetime.now(UTC) + timedelta(days=1)
        )
        tokens.append(token)
    
    # Test forward relationship (token -> user)
    for token in tokens:
        fetched_user = await token.user
        assert fetched_user == user
        assert fetched_user.email == user.email
    
    # Test reverse relationship (user -> tokens)
    user_tokens = await user.tokens.all()
    assert len(user_tokens) == 3
    assert all(token in user_tokens for token in tokens)
    
    # Test filtering tokens by user
    filtered_tokens = await Token.filter(user=user)
    assert len(filtered_tokens) == 3
    assert all(token in filtered_tokens for token in tokens)

@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_expiration():
    # Create a user
    user = await User.create(
        email="expiry_test@example.com",
        password="secret",
        name="Expiry Test User",
        account_uuid=generate_id("acc")
    )
    
    # Create an expired token
    expired_at = datetime.now(UTC) - timedelta(days=1)
    expired_token = await Token.create(
        user=user,
        token=generate_unique_token(),
        expires_at=expired_at
    )
    
    # Create a valid token
    valid_until = datetime.now(UTC) + timedelta(days=1)
    valid_token = await Token.create(
        user=user,
        token=generate_unique_token(),
        expires_at=valid_until
    )
    
    # Verify token expiration
    now = datetime.now(UTC)
    assert naive_to_utc(expired_token.expires_at) < now
    assert naive_to_utc(valid_token.expires_at) > now

@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_uniqueness():
    # Create a user
    user = await User.create(
        email="unique_test@example.com",
        password="secret",
        name="Unique Test User",
        account_uuid=generate_id("acc")
    )
    
    # Create first token
    token_value = generate_unique_token()
    await Token.create(
        user=user,
        token=token_value,
        expires_at=datetime.now(UTC) + timedelta(days=1)
    )
    
    # Attempt to create token with same value should fail
    with pytest.raises(Exception):
        await Token.create(
            user=user,
            token=token_value,  # Same token value
            expires_at=datetime.now(UTC) + timedelta(days=1)
        )
