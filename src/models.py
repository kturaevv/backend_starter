import datetime
from typing import Any

from pydantic.dataclasses import dataclass as pydantic_dataclass
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column, registry
from sqlalchemy.orm import Mapped as M

from src.constants import Fields
from src.database import metadata


class BaseModel(
    MappedAsDataclass,
    DeclarativeBase,
    dataclass_callable=pydantic_dataclass,
):
    """Base database model with common configs and columns application wide."""

    __abstract__ = True
    metadata = metadata

    registry = registry(
        type_annotation_map={
            Fields.STR_255: String(255),
        }
    )
    created_at: M[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: M[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    @classmethod
    def table_name(cls) -> Any:
        return cls.__tablename__

    @property
    def data(cls) -> dict[str, Any]:
        return cls.__dict__
