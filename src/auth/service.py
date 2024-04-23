import uuid
from datetime import datetime, timedelta

from pydantic import UUID4

from src import utils
from src.auth.config import auth_settings
from src.auth.exceptions import InvalidCredentials
from src.auth.models import AuthRefreshTokenModel, AuthUserModel, UserRoles
from src.auth.schemas import AuthUser, BaseUser
from src.auth.security import hash_password, verify_password
from src.database import execute, fetch_one


async def create_user_with_password(user: AuthUser) -> BaseUser | None:
    values = (
        user.email,
        hash_password(user.password),
        datetime.now(),
    )
    query = f"INSERT INTO {AuthUserModel.table_name()}(email, password, created_at) VALUES (%s, %s, %s) RETURNING *;"  # noqa
    data = await fetch_one(query, values)
    if not data:
        return data
    return BaseUser(**data)


async def create_user_with_password_and_role(
    user: AuthUser, role: UserRoles
) -> BaseUser | None:
    values = (user.email, hash_password(user.password), datetime.now(), role.value)
    query = f"INSERT INTO {AuthUserModel.table_name()}(email, password, created_at, role) VALUES (%s, %s, %s, %s) RETURNING *;"  # noqa
    data = await fetch_one(query, values)
    if not data:
        return data
    return BaseUser(**data)


async def create_user_with_sso(email: str) -> None:
    values = (
        email,
        datetime.now(),
    )
    query = f"INSERT INTO {AuthUserModel.table_name()}(email, created_at) VALUES (%s, %s) RETURNING *;"  # noqa
    return await execute(query, values)


async def delete_user(user_email: str) -> None:
    values = (user_email,)
    query = f"DELETE FROM {AuthUserModel.table_name()} WHERE email = %s"  # noqa
    return await execute(query, values)


async def get_user_by_id(user_id: int) -> AuthUserModel | None:
    query = f"SELECT * FROM {AuthUserModel.table_name()} WHERE id = %s"
    data = await fetch_one(query, (user_id,))
    if data is None:
        return data
    return AuthUserModel(**data)


async def get_user_by_email(email: str) -> AuthUserModel | None:
    query = f"SELECT * FROM {AuthUserModel.table_name()} WHERE email = %s"
    data = await fetch_one(query, (email,))
    if not data:
        return data
    return AuthUserModel(**data)


async def create_refresh_token(
    *, user_id: int, refresh_token: str | None = None
) -> str:
    if not refresh_token:
        refresh_token = utils.generate_random_alphanum(64)

    data = (
        uuid.uuid4(),
        refresh_token,
        datetime.now() + timedelta(seconds=auth_settings.REFRESH_TOKEN_EXP),
        user_id,
    )

    query = f"INSERT INTO {AuthRefreshTokenModel.table_name()}(uuid, refresh_token, expires_at, user_id) VALUES (%s, %s, %s, %s)"  # noqa
    await execute(query, data)

    return refresh_token


async def get_refresh_token(refresh_token: str) -> AuthRefreshTokenModel | None:
    query = (
        f"SELECT * FROM {AuthRefreshTokenModel.table_name()} WHERE refresh_token = %s;"  # noqa
    )
    data = await fetch_one(query, (refresh_token,))
    if not data:
        return None
    return AuthRefreshTokenModel(**data)


async def expire_refresh_token(refresh_token_uuid: UUID4) -> None:
    query = f"UPDATE {AuthRefreshTokenModel.table_name()} SET expires_at = %s WHERE uuid = %s;"  # noqa
    await execute(query, (datetime.now() - timedelta(days=1), refresh_token_uuid))


async def authenticate_user(auth_data: AuthUser) -> AuthUserModel:
    user: AuthUserModel | None = await get_user_by_email(auth_data.email)

    if not user:
        raise InvalidCredentials()

    if not verify_password(user.password, auth_data.password):
        raise InvalidCredentials()

    return user
