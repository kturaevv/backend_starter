import datetime
from typing import Any
from unittest.mock import MagicMock

from src.auth.config import auth_settings
from tests.base import TestClient, pytest, pytest_asyncio, status


@pytest.fixture
def mocking_datetime_now(monkeypatch: Any) -> None:
    datetime_mock = MagicMock(wrap=datetime.datetime)
    datetime_mock.now.return_value = datetime.datetime.now() + datetime.timedelta(
        days=30
    )
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


@pytest.mark.asyncio
async def test_expired_access_token_use_refresh_token(auth_client: TestClient) -> None:
    del auth_client.cookie_jar[auth_settings.ACCESS_TOKEN_KEY]
    response = await auth_client.get("/auth/me")
    assert response.status_code == status.HTTP_200_OK, response.content


@pytest_asyncio.fixture(scope="function")
async def short_session(auth_client: TestClient, mocking_datetime_now: Any) -> Any:
    yield auth_client


@pytest.mark.asyncio
async def test_new_short_session(short_session: TestClient) -> None:
    pass


@pytest.mark.asyncio
async def test_auth_invalid_after_token_is_expired(
    short_session: TestClient,
) -> None:
    pass


@pytest.mark.asyncio
async def test_auth_invalid_after_logout(
    short_session: TestClient,
) -> None:
    pass


@pytest.mark.asyncio
async def test_auth_invalid_with_expired_access_refresh_tokens(
    auth_client: TestClient,
) -> None:
    pass
