import pytest
import pytest_asyncio
from fastapi import Response

from src.config import settings
from src.main import app
from tests.conftest import TestClient


@pytest.mark.asyncio
async def test_healthcheck(client: TestClient) -> None:
    response = await client.get("/healthcheck")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_environment(client: TestClient) -> None:
    assert settings.ENVIRONMENT.is_testing, settings.ENVIRONMENT


@pytest_asyncio.fixture(scope="function")
async def share_state_endpoint() -> None:
    @app.get("/test_shared_state", include_in_schema=False)
    def _(response: Response) -> Response:
        response.set_cookie("test_shared_state", "200")
        return response


@pytest.mark.asyncio
async def test_test_isolation_setup_cookie(
    share_state_endpoint: None, client: TestClient
) -> None:
    response = await client.get("/test_shared_state")
    assert len(response.cookies.items()) == 1, response
    assert response.cookies.get("test_shared_state") == "200"


@pytest.mark.asyncio
async def test_test_isolation_test_cookie(client: TestClient) -> None:
    assert client.cookie_jar["test_shared_state"], client.cookie_jar.keys()
    assert client.cookie_jar["test_shared_state"].value == "200", client.cookie_jar

    # Clean up cookie
    del client.cookie_jar["test_shared_state"]
    assert not client.cookie_jar.get("test_shared_state", None)
