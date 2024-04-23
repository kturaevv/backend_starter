from src.auth.exceptions import (
    AuthRequired,
    EmailTaken,
    InvalidCredentials,
    RefreshTokenNotValid,
)
from src.auth.schemas import AuthUser
from tests.base import TestClient, pytest, pytest_asyncio, status


@pytest_asyncio.fixture(scope="module")
async def fake_user() -> AuthUser:
    return AuthUser(email="email@fake.com", password="123Aa!")


@pytest.mark.asyncio
async def test_user_register(client: TestClient, fake_user: AuthUser) -> None:
    resp = await client.post(
        "/auth/signup",
        json=fake_user.data,
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content


@pytest.mark.asyncio
async def test_user_register_existing(client: TestClient, fake_user: AuthUser) -> None:
    resp = await client.post(
        "/auth/signup",
        json=fake_user.data,
    )
    assert resp.status_code == EmailTaken.STATUS_CODE, resp.content
    assert resp.json()["detail"] == EmailTaken.DETAIL, resp.content


@pytest.mark.asyncio
async def test_user_register_require_password(client: TestClient) -> None:
    resp = await client.post(
        "/auth/signup",
        json={
            "email": "email@fake.com",
        },
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.content


@pytest.mark.asyncio
async def test_user_register_require_valid_email_format(
    client: TestClient, fake_user: AuthUser
) -> None:
    non_valid_email = fake_user.model_copy()
    non_valid_email.email = "nonvalidemail.com"

    resp = await client.post(
        "/auth/signup",
        json=non_valid_email.data,
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.content


@pytest.mark.asyncio
async def test_user_login(client: TestClient, fake_user: AuthUser) -> None:
    resp = await client.post(
        "/auth/signin",
        json=fake_user.data,
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content
    assert resp.json()["access_token"], resp.content
    assert resp.json()["refresh_token"], resp.content
    # assert len(resp.cookies.items()) == 1, resp.cookies


@pytest.mark.asyncio
async def test_user_login_require_auth_data(
    client: TestClient,
) -> None:
    resp = await client.post(
        "/auth/signin",
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.content


@pytest.mark.asyncio
async def test_user_login_require_password(
    client: TestClient,
) -> None:
    resp = await client.post(
        "/auth/signin",
        json={"email": "email@fake.com"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, resp.content


@pytest.mark.asyncio
async def test_user_login_require_registered_user(client: TestClient) -> None:
    resp = await client.post(
        "/auth/signin",
        json={
            "email": "not_existing@fake.com",
            "password": "123Aa!",
        },
    )
    assert resp.status_code == InvalidCredentials.STATUS_CODE, resp.content
    assert resp.json()["detail"] == InvalidCredentials.DETAIL, resp.content


@pytest.mark.asyncio
async def test_user_login_refresh_token(
    client: TestClient, fake_user: AuthUser
) -> None:
    resp = await client.put(
        "/auth/token",
        json=fake_user.data,
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content
    assert resp.json()["access_token"], resp.content
    assert resp.json()["refresh_token"], resp.content
    # assert len(resp.cookies.items()) == 1, resp.cookies


@pytest.mark.asyncio
async def test_user_logout(client: TestClient, fake_user: AuthUser) -> None:
    resp = await client.delete(
        "/auth/token",
        json=fake_user.data,
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content


@pytest.mark.asyncio
async def test_user_logout_invalidates_token(client: TestClient) -> None:
    resp = await client.delete("/auth/token")
    assert resp.status_code == RefreshTokenNotValid.STATUS_CODE, resp.content
    assert resp.json()["detail"] == RefreshTokenNotValid.DETAIL, resp.content


@pytest.mark.asyncio
async def test_user_logout_invalidates_auth(client: TestClient) -> None:
    resp = await client.get("/auth/me")
    assert resp.status_code == AuthRequired.STATUS_CODE, resp.content
    assert resp.json()["detail"] == AuthRequired.DETAIL, resp.content


@pytest.mark.asyncio
async def test_user_login_refresh_during_inactive_session(
    client: TestClient, fake_user: AuthUser
) -> None:
    resp = await client.put(
        "/auth/token",
        json=fake_user.data,
    )
    assert resp.status_code == RefreshTokenNotValid.STATUS_CODE, resp.content
    assert resp.json()["detail"] == RefreshTokenNotValid.DETAIL, resp.content


@pytest.mark.asyncio
async def test_argon2_config_migration_allow_authenticate_old_users(
    client: TestClient,
) -> None:
    pass
