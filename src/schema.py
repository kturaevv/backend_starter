import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, model_validator


def bytes_to_dict(data: Any) -> Any:
    if isinstance(data, bytes):
        try:
            decoded_data = data.decode("utf-8")
            return json.loads(decoded_data)  # type: ignore[no-any-return]
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise HTTPException(status_code=400, detail="Invalid JSON data")
    return data


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    @property
    def data(self) -> dict[str, Any]:
        "Alias for model_dump"
        return self.model_dump()

    @model_validator(mode="before")
    @classmethod
    def set_null_microseconds(cls, data: dict[Any, Any]) -> dict[str, Any]:
        data = bytes_to_dict(data)
        datetime_fields = {
            k: v.replace(microsecond=0)
            for k, v in data.items()
            if isinstance(k, datetime)
        }
        data = {**data, **datetime_fields}
        return data

    def serializable_dict(self, **kwargs: Any) -> Any:
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)
