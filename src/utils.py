import logging
import random
import string

import psycopg
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)
ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


def terminate_all_sessions(database_name: str, connection_string: str) -> None:
    with psycopg.connect(connection_string, row_factory=dict_row) as conn:
        # Get a list of all active session PIDs except the current session
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT pid FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid();
            """,
                (database_name,),
            )
            pids = cur.fetchall()

        # Terminate all these sessions
        for pid in pids:
            with conn.cursor() as cur:
                try:
                    cur.execute("SELECT pg_terminate_backend(%s);", (pid["pid"],))
                    print(f"Terminated session {pid['pid']}")
                except Exception as e:
                    print(f"Error terminating session {pid['pid']}: {str(e)}")

        print("All sessions terminated.")
