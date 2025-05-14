import pytest
from app.models.user import User
from lib.core.record.uuid import generate_id
from lib.core.authentication.passwords import verify_password

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
