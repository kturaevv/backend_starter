from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.auth import models
from src.auth.config import auth_settings
from src.auth.exceptions import InvalidToken
from src.auth.schemas import JWTData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def create_access_token(
    *,
    user: models.AuthUserModel,
    expires_delta: timedelta = timedelta(seconds=auth_settings.JWT_EXP),
) -> Any:
    jwt_data = {
        "sub": str(user.id),
        "exp": datetime.now() + expires_delta,
        "is_admin": user.is_admin,
    }
    return jwt.encode(
        jwt_data, auth_settings.JWT_SECRET, algorithm=auth_settings.JWT_ALG
    )


def decode_access_token(token: str) -> Any:
    try:
        return jwt.decode(
            token, auth_settings.JWT_SECRET, algorithms=[auth_settings.JWT_ALG]
        )
    except JWTError:
        raise InvalidToken()


async def retrieve_access_token_from_cookies(request: Request) -> str | None:
    return request.cookies.get(auth_settings.ACCESS_TOKEN_KEY, None)


async def retrieve_refresh_token_from_cookies(request: Request) -> str | None:
    return request.cookies.get(auth_settings.REFRESH_TOKEN_KEY, None)


async def retrieve_auth_tokens(
    access_token: str | None = Depends(retrieve_access_token_from_cookies),
    refresh_token: str | None = Depends(retrieve_refresh_token_from_cookies),
) -> tuple[str | None, str | None]:
    return access_token, refresh_token


async def parse_access_token(
    token: str = Depends(retrieve_access_token_from_cookies),
) -> JWTData | None:
    if not token:
        return None

    payload = decode_access_token(token)

    return JWTData(**payload)
