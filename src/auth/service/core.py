import uuid
from datetime import datetime, timedelta
from typing import Any, Sequence

from fastapi.security import OAuth2PasswordBearer
from pydantic import UUID4

from src import utils
from src.auth.config import auth_settings
from src.auth.exceptions import InvalidCredentials
from src.auth.models import AuthRefreshTokenModel, AuthUserModel, UserRoles
from src.auth.schemas import AuthUser, BaseUser
from src.auth.security import hash_password, verify_password
from src.database import execute, fetch_one

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


async def _insert_user(query: str, values: Sequence[Any]) -> BaseUser | None:
    data = await fetch_one(query, values)
    return BaseUser(**data) if data else None


async def create_user_with_password(user: AuthUser) -> BaseUser | None:
    query = f"""
        INSERT INTO {AuthUserModel.table_name()} (email, password, created_at)
        VALUES (%s, %s, %s) RETURNING *;
    """
    values = (user.email, hash_password(user.password), datetime.now())
    return await _insert_user(query, values)


async def create_user_with_password_and_role(
    user: AuthUser, role: UserRoles
) -> BaseUser | None:
    query = f"""
        INSERT INTO {AuthUserModel.table_name()} (email, password, created_at, role)
        VALUES (%s, %s, %s, %s) RETURNING *;
    """
    values = (user.email, hash_password(user.password), datetime.now(), role.value)
    return await _insert_user(query, values)


async def create_user_with_sso(email: str) -> AuthUserModel | None:
    query = f"""
        INSERT INTO {AuthUserModel.table_name()} (email, password, created_at)
        VALUES (%s, %s, %s) RETURNING *;
    """
    values = (email, utils.generate_random_password(), datetime.now())
    data = await fetch_one(query, values)
    return AuthUserModel(**data) if data else None


async def delete_user(user_email: str) -> None:
    query = f"DELETE FROM {AuthUserModel.table_name()} WHERE email = %s;"
    await execute(query, (user_email,))


async def get_user_by_id(user_id: int) -> AuthUserModel | None:
    query = f"SELECT * FROM {AuthUserModel.table_name()} WHERE id = %s;"
    data = await fetch_one(query, (user_id,))
    return AuthUserModel(**data) if data else None


async def get_user_by_email(email: str) -> AuthUserModel | None:
    query = f"SELECT * FROM {AuthUserModel.table_name()} WHERE email = %s;"
    data = await fetch_one(query, (email,))
    return AuthUserModel(**data) if data else None


async def create_refresh_token(user_id: int, refresh_token: str | None = None) -> str:
    if not refresh_token:
        refresh_token = utils.generate_random_alphanum(64)

    data = (
        uuid.uuid4(),
        refresh_token,
        datetime.now() + timedelta(seconds=auth_settings.REFRESH_TOKEN_EXP),
        user_id,
    )

    query = f"""
        INSERT INTO {AuthRefreshTokenModel.table_name()}
            (uuid, refresh_token, expires_at, user_id)
        VALUES (%s, %s, %s, %s);
    """
    await execute(query, data)
    return refresh_token


async def get_refresh_token(refresh_token: str) -> AuthRefreshTokenModel | None:
    query = f"""
        SELECT * FROM {AuthRefreshTokenModel.table_name()} WHERE refresh_token = %s;
    """
    data = await fetch_one(query, (refresh_token,))
    return AuthRefreshTokenModel(**data) if data else None


async def expire_refresh_token(refresh_token_uuid: UUID4) -> None:
    query = f"""
        UPDATE {AuthRefreshTokenModel.table_name()} SET expires_at = %s WHERE uuid = %s;
    """
    await execute(query, (datetime.now() - timedelta(days=1), refresh_token_uuid))


async def authenticate_user(auth_data: AuthUser) -> AuthUserModel:
    user: AuthUserModel | None = await get_user_by_email(auth_data.email)
    if not user or not verify_password(user.password, auth_data.password):
        raise InvalidCredentials()
    return user
