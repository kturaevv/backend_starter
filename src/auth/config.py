import argon2
from fastapi_sso import GoogleSSO
from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    JWT_ALG: str
    JWT_SECRET: str
    JWT_EXP: int = 60 * 5  # 5 minutes

    ACCESS_TOKEN_KEY: str = "accessToken"
    ACCESS_TOKEN_EXP: int = 60 * 15  # 15 minutes

    REFRESH_TOKEN_KEY: str = "refreshToken"
    REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 21  # 21 days

    SECURE_COOKIES: bool = True

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    password_hasher: argon2.PasswordHasher = argon2.PasswordHasher()


auth_settings = AuthConfig()  # type: ignore

google_sso = GoogleSSO(
    auth_settings.GOOGLE_CLIENT_ID,
    auth_settings.GOOGLE_CLIENT_SECRET,
    auth_settings.GOOGLE_REDIRECT_URI,
)
