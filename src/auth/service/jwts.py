from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from src.auth.config import auth_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def create_access_token(
    *,
    user_id: Optional[str] = None,
    is_admin: bool = False,
    is_registered: bool = False,
    expires_delta: timedelta = timedelta(seconds=auth_settings.JWT_EXP),
) -> Any:
    """
    Create an access token for both registered and non-registered users.

    :param user_id: ID of the user (None for non-registered users)
    :param is_admin: Boolean flag for admin status
    :param is_registered: Boolean flag indicating if the user is registered
    :param expires_delta: Expiration time for the token
    :return: Encoded JWT token
    """
    jwt_data = {
        "sub": str(user_id) if user_id else "non_registered_user",
        "exp": datetime.now() + expires_delta,
        "is_admin": is_admin,
        "is_registered": is_registered,
    }
    return jwt.encode(
        jwt_data, auth_settings.JWT_SECRET, algorithm=auth_settings.JWT_ALG
    )
