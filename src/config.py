from typing import Any, Optional

from pydantic import (
    BaseModel,
    PostgresDsn,
    RedisDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings

from src.constants import Environment


class PostgresURL(BaseModel):
    port: Optional[int] = None
    host: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    db_name: Optional[str] = None

    def with_db(self) -> str:
        if self.db_name:
            return self.without_db() + "/" + self.db_name
        else:
            raise Exception("No database name has been provided!")

    def without_db(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}"


class Config(BaseSettings):
    REDIS_URL: RedisDsn

    SITE_DOMAIN: str

    ENVIRONMENT: Environment = Environment.LOCAL

    SENTRY_DSN: str | None = None

    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str]

    APP_VERSION: str = "1"

    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    POSTGRES_PASSWORD: str

    database: PostgresURL = PostgresURL()

    @model_validator(mode="after")
    def validate_sentry_non_local(self) -> "Config":
        if self.ENVIRONMENT.is_deployed and not self.SENTRY_DSN:
            raise ValueError("Sentry is not set")

        return self

    @model_validator(mode="after")
    def validate_database(self) -> "Config":
        self.database = PostgresURL(
            db_name=self.POSTGRES_DB,
            username=self.POSTGRES_USER,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            password=self.POSTGRES_PASSWORD,
        )
        return self

    @computed_field  # type: ignore[misc]
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        if self.database:
            return PostgresDsn(self.database.with_db())
        raise Exception("Database URL is not valid!")


settings = Config()  # type: ignore[call-arg]

app_configs: dict[str, Any] = {"title": "Core API"}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs
