from datetime import datetime, timedelta
from typing import Any

from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from src.auth import models
from src.auth.config import auth_settings

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
