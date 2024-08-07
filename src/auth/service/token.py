from src.auth.config import auth_settings
from src.auth.schemas import CookieParameters
from src.config import settings


def get_refresh_token_settings(
    refresh_token: str,
    expired: bool = False,
) -> CookieParameters:
    base_cookie = CookieParameters(
        key=auth_settings.REFRESH_TOKEN_KEY,
        httponly=True,
        samesite="none",
        secure=auth_settings.SECURE_COOKIES,
        domain=settings.SITE_DOMAIN,
    )

    if expired:
        return base_cookie

    base_cookie.value = refresh_token
    base_cookie.max_age = auth_settings.REFRESH_TOKEN_EXP
    return base_cookie


def get_access_token_settings(
    token_value: str,
    expired: bool = False,
) -> CookieParameters:
    base_cookie = CookieParameters(
        key=auth_settings.ACCESS_TOKEN_KEY,
        httponly=True,
        samesite="none",
        secure=auth_settings.SECURE_COOKIES,
        domain=settings.SITE_DOMAIN,
    )

    if expired:
        return base_cookie

    base_cookie.value = token_value
    base_cookie.max_age = auth_settings.ACCESS_TOKEN_EXP
    return base_cookie
