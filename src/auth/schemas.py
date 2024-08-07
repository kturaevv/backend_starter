import re
import typing
from datetime import datetime

from pydantic import EmailStr, Field, field_validator
from typing_extensions import Annotated

from src.schema import CustomModel

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


class BaseUser(CustomModel):
    email: EmailStr


class AuthUser(BaseUser):
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol"
            )
        return password


class JWTData(CustomModel):
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AccessTokenResponse(CustomModel):
    access_token: str
    refresh_token: str


class CookieParameters(CustomModel):
    key: str
    value: str = ""
    max_age: int | None = None
    expires: datetime | str | int | None = None
    path: str = "/"
    domain: str | None = None
    secure: bool = False
    httponly: bool = False
    samesite: typing.Literal["lax", "strict", "none"] | None = "lax"


class DomainNameValidator(CustomModel):
    domain: Annotated[
        str,
        Field(
            pattern=r"^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$",
            description="A valid domain name without path",
        ),
    ]
