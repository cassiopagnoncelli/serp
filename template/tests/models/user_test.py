import pytest
from app.models.user import User
from app.models.token import Token
from lib.core.record.uuid import generate_id
from lib.core.authentication.passwords import verify_password, encrypt_password
from datetime import datetime, timedelta, UTC

@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user():
    password = "secret"
    user = await User.create(
        email="test@example.com",
        password=password,
        name="Test User",
        account_uuid=generate_id("acc")
    )
    assert user.id is not None
    assert user.uuid.startswith("usr_")
    assert user.email == "test@example.com"
    assert verify_password(password, user.enc_password)
    assert user.name == "Test User"
    assert user.account_uuid.startswith("acc_")

@pytest.mark.unit
@pytest.mark.asyncio
async def test_uuid_is_unique():
    user1 = await User.create(
        email="a@example.com",
        password="pw1",
        name="A",
        account_uuid=generate_id("acc")
    )
    user2 = await User.create(
        email="b@example.com",
        password="pw2",
        name="B",
        account_uuid=generate_id("acc")
    )
    assert user1.uuid != user2.uuid

@pytest.mark.unit
@pytest.mark.asyncio
async def test_email_unique_constraint():
    await User.create(
        email="unique@example.com",
        password="pw",
        name="U",
        account_uuid=generate_id("acc")
    )
    with pytest.raises(Exception):
        await User.create(
            email="unique@example.com",
            password="pw2",
            name="U2",
            account_uuid=generate_id("acc")
        )

@pytest.mark.unit
@pytest.mark.asyncio
async def test_change_password():
    # Create initial user
    initial_password = "initial_secret"
    user = await User.create(
        email="change_pw@example.com",
        password=initial_password,
        name="Password Changer",
        account_uuid=generate_id("acc")
    )
    
    # Verify initial password works
    assert verify_password(initial_password, user.enc_password)
    
    # Change password
    new_password = "new_secret"
    await user.update(enc_password=encrypt_password(new_password))
    
    # Verify new password works and old one doesn't
    assert verify_password(new_password, user.enc_password)
    assert not verify_password(initial_password, user.enc_password)

@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_user_info():
    # Create initial user
    user = await User.create(
        email="update@example.com",
        password="secret",
        name="Original Name",
        account_uuid=generate_id("acc")
    )
    
    # Update user information
    new_name = "Updated Name"
    await user.update(name=new_name)
    
    # Verify the update
    updated_user = await User.get(uuid=user.uuid)
    assert updated_user.name == new_name
    assert updated_user.email == user.email  # Other fields should remain unchanged

@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_user():
    # Create a user
    user = await User.create(
        email="delete@example.com",
        password="secret",
        name="To Be Deleted",
        account_uuid=generate_id("acc")
    )
    
    # Verify user exists
    assert await User.filter(uuid=user.uuid).exists()
    
    # Delete the user
    await user.delete()
    
    # Verify user no longer exists
    assert not await User.filter(uuid=user.uuid).exists()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_query_users():
    # Create multiple users
    users = []
    for i in range(3):
        user = await User.create(
            email=f"user{i}@example.com",
            password="secret",
            name=f"User {i}",
            account_uuid=generate_id("acc")
        )
        users.append(user)
    
    # Test getting all users
    all_users = await User.all()
    assert len(all_users) >= 3  # At least our 3 users
    
    # Test getting a specific user by UUID
    specific_user = await User.get(uuid=users[0].uuid)
    assert specific_user.email == users[0].email
    assert specific_user.name == users[0].name
    
    # Test filtering users
    filtered_users = await User.filter(name__startswith="User")
    assert len(filtered_users) >= 3  # At least our 3 users
    
    # Clean up
    await User.delete_all()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_user_token_relationship():
    # Create a user
    user = await User.create(
        email="token_relation@example.com",
        password="secret",
        name="Token Relation User",
        account_uuid=generate_id("acc")
    )
    
    # Create multiple tokens for the user
    tokens = []
    for i in range(3):
        token = await Token.create(
            user=user,
            token=f"test_token_{generate_id('tkn')}",
            expires_at=datetime.now(UTC) + timedelta(days=1)
        )
        tokens.append(token)
    
    # Test getting all tokens for a user
    user_tokens = await user.tokens.all()
    assert len(user_tokens) == 3
    assert all(token in user_tokens for token in tokens)
    
    # Test filtering tokens
    active_tokens = await user.tokens.filter(expires_at__gt=datetime.now(UTC))
    assert len(active_tokens) == 3
    
    # Test token creation through relationship
    new_token = await Token.create(  # Use Token.create instead of user.tokens.create
        user=user,
        token=f"test_token_{generate_id('tkn')}",
        expires_at=datetime.now(UTC) + timedelta(days=1)
    )
    assert new_token.user == user
    
    # Verify token count after creation
    updated_tokens = await user.tokens.all()
    assert len(updated_tokens) == 4
    
    # Test token deletion through relationship
    await Token.filter(id=new_token.id).delete()  # Use Token.filter instead of user.tokens.filter
    final_tokens = await user.tokens.all()
    assert len(final_tokens) == 3
