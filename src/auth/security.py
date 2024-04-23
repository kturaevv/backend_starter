import argon2

from src.auth.config import auth_settings


def hash_password(plain_password: str) -> str:
    return auth_settings.password_hasher.hash(plain_password)


def verify_password(password_hash: str, plain_password: str) -> bool:
    try:
        auth_settings.password_hasher.verify(password_hash, plain_password)
    except argon2.exceptions.InvalidHashError:
        return False
    return True
