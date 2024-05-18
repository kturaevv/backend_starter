from src.auth.exceptions import AuthorizationFailed, AuthRequired
from tests.base import TestClient, pytest, status


@pytest.mark.asyncio
async def test_user_authorization_anon_user(client: TestClient) -> None:
    resp = await client.get("/auth/me")
    assert resp.status_code == AuthRequired.STATUS_CODE, resp.content
    assert resp.json()["detail"] == AuthRequired.DETAIL, resp.content


@pytest.mark.asyncio
async def test_user_authorization_auth_user(auth_client: TestClient) -> None:
    resp = await auth_client.get("/auth/me")
    assert resp.status_code == status.HTTP_200_OK, resp.content


@pytest.mark.asyncio
async def test_user_authorization_post_logout(auth_client: TestClient) -> None:
    resp = await auth_client.delete("/auth/token")
    assert resp.status_code == status.HTTP_200_OK, resp.content

    resp = await auth_client.get("/auth/me")
    assert resp.status_code == AuthRequired.STATUS_CODE, resp.content
    assert resp.json()["detail"] == AuthRequired.DETAIL, resp.content


@pytest.mark.asyncio
async def test_authorization_admin_user_restricted(auth_client: TestClient) -> None:
    resp = await auth_client.get("/auth/admin")
    assert resp.status_code == AuthorizationFailed.STATUS_CODE, resp.content
    assert resp.json()["detail"] == AuthorizationFailed.DETAIL, resp.content


@pytest.mark.asyncio
async def test_authorization_admin_user(auth_admin_client: TestClient) -> None:
    resp = await auth_admin_client.get("/auth/admin")
    assert resp.status_code == status.HTTP_200_OK, resp.content
    assert resp.json() == "ok", resp.content


@pytest.mark.asyncio
async def test_authorization_admin_user_has_basic_auth(
    auth_admin_client: TestClient,
) -> None:
    resp = await auth_admin_client.get("/auth/me")
    assert resp.status_code == status.HTTP_200_OK, resp.content
