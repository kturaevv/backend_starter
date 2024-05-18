from typing import Any, AsyncGenerator

import pytest_asyncio
from async_asgi_testclient import TestClient
from fastapi import status

from src.auth.models import UserRoles
from src.auth.schemas import AuthUser
from src.auth.service.core import create_user_with_password_and_role, delete_user
from src.utils import generate_random_password


@pytest_asyncio.fixture(scope="function")
async def register_admin_user() -> AsyncGenerator[AuthUser, None]:
    """Setup a temporary test database and configure the application to use it."""
    admin_user = AuthUser(email="test@admin.we", password=generate_random_password())
    await create_user_with_password_and_role(admin_user, UserRoles.ADMIN)
    yield admin_user
    await delete_user(admin_user.email)


@pytest_asyncio.fixture(scope="function")
async def auth_admin_client(client: TestClient, register_admin_user: AuthUser) -> Any:
    admin_user = register_admin_user
    response = await client.post(
        "/auth/signin",
        json={"email": admin_user.email, "password": admin_user.password},
    )
    assert response.status_code == status.HTTP_200_OK, response.content

    yield client

    client.cookie_jar.clear()
