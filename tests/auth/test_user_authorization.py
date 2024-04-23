from src.auth.exceptions import AuthRequired
from tests.base import TestClient, pytest, status


@pytest.mark.asyncio
async def test_basic_user_authorization(auth_client: TestClient) -> None:
    resp = await auth_client.get("/auth/me")
    assert resp.status_code == status.HTTP_200_OK, resp.content


@pytest.mark.asyncio
async def test_basic_user_authorization_post_logout(auth_client: TestClient) -> None:
    resp = await auth_client.delete("/auth/token")
    assert resp.status_code == status.HTTP_200_OK, resp.content

    resp = await auth_client.get("/auth/me")
    assert resp.status_code == AuthRequired.STATUS_CODE, resp.content
    assert resp.json()["detail"] == AuthRequired.DETAIL, resp.content


@pytest.mark.asyncio
async def test_basic_user_authorization_requires_auth_data(client: TestClient) -> None:
    resp = await client.get("/auth/me")
    assert resp.status_code == AuthRequired.STATUS_CODE, resp.content
    assert resp.json()["detail"] == AuthRequired.DETAIL, resp.content
