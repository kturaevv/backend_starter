from datetime import datetime
from typing import Any

from fastapi import Cookie, Depends, Response

from src.auth import service
from src.auth.config import auth_settings
from src.auth.exceptions import (
    RefreshTokenNotValid,
)
from src.auth.models import AuthRefreshTokenModel, AuthUserModel
from src.auth.schemas import JWTData

from .access_token import parse_access_token


def _is_valid_refresh_token(db_refresh_token: AuthRefreshTokenModel) -> Any:
    return datetime.now() <= db_refresh_token.expires_at


async def valid_refresh_token(
    refresh_token: str = Cookie(..., alias=auth_settings.REFRESH_TOKEN_KEY),
) -> AuthRefreshTokenModel:
    db_refresh_token = await service.get_refresh_token(refresh_token)

    if not db_refresh_token:
        raise RefreshTokenNotValid()

    if not _is_valid_refresh_token(db_refresh_token):
        raise RefreshTokenNotValid()

    return db_refresh_token


async def valid_refresh_token_user(
    refresh_token: AuthRefreshTokenModel = Depends(valid_refresh_token),
) -> AuthUserModel:
    user = await service.get_user_by_id(refresh_token.user_id)
    if not user:
        raise RefreshTokenNotValid()

    return user


async def valid_refresh_token_user_token(
    refresh_token: AuthRefreshTokenModel = Depends(valid_refresh_token),
) -> tuple[AuthUserModel, AuthRefreshTokenModel]:
    user = await service.get_user_by_id(refresh_token.user_id)
    if not user:
        raise RefreshTokenNotValid()

    return user, refresh_token


async def refresh_access_token(
    response: Response,
    access_token: JWTData | None = Depends(parse_access_token),
    user: AuthUserModel = Depends(valid_refresh_token_user),
) -> JWTData | None:
    if access_token:
        return access_token

    access_token_value = service.jwts.create_access_token(
        user_id=user.id, is_admin=user.is_admin
    )
    response.set_cookie(
        **service.token.get_access_token_settings(access_token_value).data
    )
    return access_token
