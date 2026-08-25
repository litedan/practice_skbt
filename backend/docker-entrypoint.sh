#!/bin/sh
set -e

wait_for_tcp() {
  host="$1"
  port="$2"
  echo "Waiting for ${host}:${port}..."
  until python - <<PY
import socket
import sys

host = "${host}"
port = int("${port}")
try:
    with socket.create_connection((host, port), timeout=2):
        pass
except OSError:
    sys.exit(1)
PY
  do
    sleep 1
  done
  echo "${host}:${port} is ready"
}

wait_for_tcp "${MAIN_DB_HOST:-hr_postgres}" "${MAIN_DB_PORT:-5432}"
wait_for_tcp "${LOG_DB_HOST:-hr_logs_postgres}" "${LOG_DB_PORT:-5432}"

echo "Applying MainBD migrations..."
python - <<'PY'
import asyncio
import os
import subprocess

import asyncpg


async def prepare() -> None:
    conn = await asyncpg.connect(
        user=os.environ["MAIN_DB_USER"],
        password=os.environ["MAIN_DB_PASSWORD"],
        database=os.environ["MAIN_DB_NAME"],
        host=os.environ.get("MAIN_DB_HOST", "hr_postgres"),
        port=int(os.environ.get("MAIN_DB_PORT", "5432")),
    )
    try:
        has_users = await conn.fetchval(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'app' AND table_name = 'users'
            """
        )
        has_version = await conn.fetchval(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'app' AND table_name = 'alembic_version'
            """
        )
        if has_users and not has_version:
            print(
                "Existing MainBD schema without Alembic history; stamping 001_main_schema"
            )
            subprocess.check_call(
                ["alembic", "-x", "db=main", "stamp", "001_main_schema"]
            )
    finally:
        await conn.close()


asyncio.run(prepare())
PY
alembic -x db=main upgrade head

echo "Applying LogBD migrations..."
alembic -c alembic_log.ini -x db=log upgrade head

echo "Ensuring dev users (@kedo.local)..."
python scripts/ensure_dev_users.py

echo "Starting API..."
exec "$@"
