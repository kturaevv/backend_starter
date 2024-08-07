import datetime
import enum
from typing import Optional
from uuid import UUID as uuid_type

from sqlalchemy import ForeignKey, types
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import text

from src.constants import Fields
from src.models import BaseModel


class UserRoles(enum.Enum):
    USER = 1
    ADMIN = 2
    AGENCY = 3


class AuthUserModel(BaseModel):
    __tablename__ = "auth_user"

    id: M[int] = mapped_column(primary_key=True)
    email: M[Fields.STR_255] = mapped_column(nullable=False)
    password: M[Optional[Fields.STR_255]] = mapped_column(nullable=True)
    domain_information: M[Optional[int]] = mapped_column(
        ForeignKey("domain_information.id", ondelete="NO ACTION"), nullable=True
    )
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


class SubscriptionType(enum.Enum):
    BASIC = 1


class DomainInformationModel(BaseModel):
    __tablename__ = "domain_information"

    id: M[int] = mapped_column(primary_key=True)
    domain_name: M[Fields.STR_255] = mapped_column(nullable=False)
    subscription_type: M[int] = mapped_column(nullable=False)
    is_paid: M[bool] = mapped_column(nullable=False, default=False)
