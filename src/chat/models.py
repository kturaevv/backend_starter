import enum
from uuid import UUID as uuid_type

from sqlalchemy import ForeignKey, types
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column

from src.models import BaseModel


class SenderType(enum.Enum):
    AI = 1
    Support = 2


class ChatModel(BaseModel):
    __tablename__ = "chat"

    id: M[int] = mapped_column(primary_key=True)
    client_id: M[int] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False
    )


class MessagesModel(BaseModel):
    __tablename__ = "messages"

    id: M[uuid_type] = mapped_column(types.Uuid, primary_key=True, init=False)
    chat_id: M[int] = mapped_column(
        ForeignKey("chat.id", ondelete="CASCADE"), nullable=False
    )
    sender_type: M[int] = mapped_column(nullable=False)
    message: M[str] = mapped_column(nullable=False)
