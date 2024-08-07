import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Sequence

import psycopg
import psycopg.rows
from psycopg_pool import AsyncConnectionPool
from sqlalchemy import MetaData

from src.config import settings

metadata = MetaData()

PG_POOL: AsyncConnectionPool = None  # type: ignore


@asynccontextmanager
async def db_cursor() -> AsyncGenerator[psycopg.AsyncCursor[dict[str, Any]], None]:
    async with PG_POOL.connection() as conn:
        async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            yield cur


async def execute(query: str, values: Sequence[Any] | None = None) -> None:
    async with db_cursor() as cur:
        await cur.execute(query, values)


async def fetch_all(query: str, values: Sequence[Any] | None = None) -> Sequence[Any]:
    async with db_cursor() as cur:
        await cur.execute(query, values)
        return await cur.fetchall()


async def fetch_one(query: str, values: Sequence[Any] | None = None) -> Any | None:
    async with db_cursor() as cur:
        res = await cur.execute(query, values)
        return await res.fetchone()


async def check_db_connection_task() -> None:
    logging.info("Using polling for connectivity status.")

    try:
        async with await psycopg.AsyncConnection.connect(
            settings.database.with_db()
        ) as conn:
            while True:
                try:
                    await conn.execute("SELECT 1")
                    logging.info("Database connection: OK")
                except psycopg.OperationalError as e:
                    logging.error(f"We lost our database connection: {e}")
                    # Break the loop and allow graceful shutdown or reconnection logic
                    break
                await asyncio.sleep(60.0)  # Check every 60 seconds
    except asyncio.CancelledError:
        logging.info("Database connection monitoring task was cancelled.")
        raise
    except Exception as e:
        logging.error(f"Failed to establish database connection: {e}")


async def check_db_connection_fd() -> None:
    logging.info("Using connection File Descriptor for connectivity status.")

    event = asyncio.Event()
    loop = asyncio.get_event_loop()
    conn = await psycopg.AsyncConnection.connect(settings.database.with_db())

    loop.add_reader(conn.fileno(), event.set)

    while True:
        try:
            await asyncio.wait_for(event.wait(), 60.0)
        except asyncio.TimeoutError:
            continue  # No FD activity detected in one minute

        # Activity detected. Is the connection still ok?
        try:
            await conn.execute("SELECT 1")
            logging.info("Database connection: OK")
        except psycopg.OperationalError as e:
            logging.error(f"We lost our database connection: {e}")
            sys.exit(1)
