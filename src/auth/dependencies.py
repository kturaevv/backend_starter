from datetime import datetime
from typing import Any

from fastapi import Cookie, Depends, Response

from src.auth import jwt, schemas, service, utils
from src.auth.config import auth_settings
from src.auth.exceptions import (
    AuthorizationFailed,
    AuthRequired,
    EmailTaken,
    RefreshTokenNotValid,
)
from src.auth.jwt import parse_access_token
from src.auth.models import AuthRefreshTokenModel, AuthUserModel
from src.auth.schemas import JWTData


def _is_valid_refresh_token(db_refresh_token: AuthRefreshTokenModel) -> Any:
    return datetime.now() <= db_refresh_token.expires_at


async def valid_email_not_taken(user: schemas.AuthUser) -> schemas.AuthUser:
    if await service.get_user_by_email(user.email):
        raise EmailTaken()

    return user


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

    access_token_value = jwt.create_access_token(user=user)
    response.set_cookie(**utils.get_access_token_settings(access_token_value).data)
    return access_token


async def parse_tokens(
    response: Response,
    tokens: tuple[str | None, str | None] = Depends(jwt.retrieve_auth_tokens),
) -> JWTData | None:
    access_token, refresh_token = tokens
    if not access_token and not refresh_token:
        return None

    if access_token:
        return await jwt.parse_access_token(access_token)

    if refresh_token:
        try:
            _token = await valid_refresh_token(refresh_token)
        except RefreshTokenNotValid:
            raise AuthRequired()

        user = await service.get_user_by_id(_token.user_id)

        if not user:
            raise AuthRequired()

        new_access_token = jwt.create_access_token(user=user)
        response.set_cookie(**utils.get_access_token_settings(new_access_token).data)

        payload = jwt.decode_access_token(new_access_token)

    return JWTData(**payload)


async def valid_authenticated_user(
    access_token: JWTData | None = Depends(parse_tokens),
) -> JWTData:
    if not access_token:
        raise AuthRequired()

    return access_token


async def valid_admin_user(
    token: JWTData = Depends(parse_tokens),
) -> JWTData:
    if not token.is_admin:
        raise AuthorizationFailed()

    return token
