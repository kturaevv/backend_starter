from fastapi import Depends, Response

from src.auth import schemas, service
from src.auth.exceptions import (
    AuthorizationFailed,
    AuthRequired,
    EmailTaken,
    RefreshTokenNotValid,
)
from src.auth.schemas import JWTData

from .access_token import (
    decode_access_token,
    parse_access_token,
    retrieve_auth_tokens,
)
from .refresh_token import valid_refresh_token


async def _parse_tokens(
    response: Response,
    tokens: tuple[str | None, str | None] = Depends(retrieve_auth_tokens),
) -> JWTData | None:
    access_token, refresh_token = tokens
    if not access_token and not refresh_token:
        raise AuthRequired()

    if access_token:
        return await parse_access_token(access_token)

    if refresh_token:
        try:
            _token = await valid_refresh_token(refresh_token)
        except RefreshTokenNotValid:
            raise AuthRequired()

        user = await service.get_user_by_id(_token.user_id)

        if not user:
            raise AuthRequired()

        new_access_token = service.jwts.create_access_token(user=user)
        response.set_cookie(
            **service.token.get_access_token_settings(new_access_token).data
        )

        payload = decode_access_token(new_access_token)

    return JWTData(**payload)


async def email_not_taken(user: schemas.AuthUser) -> schemas.AuthUser:
    if await service.get_user_by_email(user.email):
        raise EmailTaken()

    return user


async def valid_authenticated_user(
    access_token: JWTData | None = Depends(_parse_tokens),
) -> JWTData:
    if not access_token:
        raise AuthRequired()

    return access_token


async def valid_admin_user(
    token: JWTData = Depends(valid_authenticated_user),
) -> JWTData:
    if not token.is_admin:
        raise AuthorizationFailed()

    return token
