import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import redis.asyncio as aioredis
import sentry_sdk
from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool
from starlette.middleware.cors import CORSMiddleware

from src import caching, database
from src.auth.router import router as auth_router
from src.config import app_configs, settings


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator[None, None]:
    database.PG_POOL = AsyncConnectionPool(
        conninfo=settings.database.with_db(), open=False
    )
    # Startup
    await database.PG_POOL.open()
    await database.PG_POOL.wait()

    if not settings.ENVIRONMENT.is_testing:
        asyncio.create_task(database.check_db_connection_task())

    redis_pool = aioredis.ConnectionPool.from_url(
        str(settings.REDIS_URL), max_connections=10, decode_responses=True
    )
    caching.redis_client = aioredis.Redis(connection_pool=redis_pool)

    yield

    await redis_pool.disconnect()
    await database.PG_POOL.close()


app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE"),
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/env", include_in_schema=False)
async def env() -> dict[Any, Any]:
    return settings.model_dump()


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
