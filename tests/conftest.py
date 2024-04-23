import os
from typing import Any, AsyncGenerator

import psycopg
import pytest_asyncio
from async_asgi_testclient import TestClient

from src import config
from src.auth.schemas import AuthUser
from src.auth.service import create_user_with_password, delete_user
from src.main import app
from tests import utils
from tests.base import status


@pytest_asyncio.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    """Setup a temporary test database and configure the application to use it."""
    database_name: str = utils.generate_database_name()
    config.settings.database.db_name = database_name

    conn = psycopg.connect(config.settings.database.without_db(), autocommit=True)
    try:
        conn.execute(f"CREATE DATABASE {database_name}")
    finally:
        conn.close()

    os.environ["POSTGRES_DB"] = config.settings.database.db_name
    os.system("alembic upgrade head")

    yield

    os.system("alembic downgrade base")

    try:
        conn = psycopg.connect(config.settings.database.without_db(), autocommit=True)
    finally:
        conn.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def client(setup_database: Any) -> AsyncGenerator[TestClient, None]:
    """
    Create a TestClient for testing endpoints.

    Note: Test client is **NOT** atomic! Application client will hold state,
        like jwt tokens between tests!
    """
    host, port = "127.0.0.1", "9000"
    scope = {"client": (host, port)}
    async with TestClient(app, scope=scope) as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="function")
async def create_user() -> Any:
    user = AuthUser(email="some@email.com", password="S1mpl@Password")
    await create_user_with_password(user)
    yield user
    await delete_user(user.email)


@pytest_asyncio.fixture(scope="function")
async def auth_client(client: TestClient, create_user: AuthUser) -> Any:
    response = await client.post("/auth/signin", json=create_user.data)
    assert response.status_code == status.HTTP_200_OK, response.content

    yield client

    client.cookie_jar.clear()
