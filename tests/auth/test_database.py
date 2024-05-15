import time

from src.auth.models import UserRoles
from src.auth.schemas import AuthUser
from src.auth.service.domain import (
    create_user_with_password,
    create_user_with_password_and_role,
    get_user_by_email,
)
from tests.base import TestClient, pytest


@pytest.mark.asyncio
async def test_user_creation_with_roles(client: TestClient) -> None:
    regular_user = AuthUser(email="email123@fake.com", password="123Aa!")
    admin_user = AuthUser(email="admin_email@fake.com", password="123Aa!")

    await create_user_with_password(regular_user)
    await create_user_with_password_and_role(admin_user, UserRoles.ADMIN)

    time.sleep(0.1)

    regular_user_model = await get_user_by_email(regular_user.email)
    admin_user_model = await get_user_by_email(admin_user.email)

    assert regular_user_model and admin_user_model
    assert regular_user_model.role == UserRoles.USER.value
    assert regular_user_model.is_admin is False
    assert admin_user_model.is_admin is True
