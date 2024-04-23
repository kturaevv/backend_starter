import datetime
import enum
from uuid import UUID as uuid_type

from sqlalchemy import ForeignKey, types
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import text

from src.models import BaseModel


class UserRoles(enum.Enum):
    USER = 1
    ADMIN = 2
    AGENCY = 3


class AuthUserModel(BaseModel):
    __tablename__ = "auth_user"

    id: M[int] = mapped_column(primary_key=True)
    email: M[str] = mapped_column(nullable=False)
    password: M[str] = mapped_column(nullable=True)
    role: M[int] = mapped_column(
        nullable=False,
        server_default=text(
            str(UserRoles.USER.value),
        ),
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRoles.ADMIN.value


class AuthRefreshTokenModel(BaseModel):
    __tablename__ = "auth_refresh_token"

    uuid: M[uuid_type] = mapped_column(types.Uuid, primary_key=True, init=False)
    user_id: M[int] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False
    )
    refresh_token: M[str] = mapped_column(nullable=False)
    expires_at: M[datetime.datetime] = mapped_column(nullable=False)
