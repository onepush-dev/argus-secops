#!/bin/sh
# Railway start wrapper for Argus (api | worker). Runs as root, then execs the upstream entrypoint as uid 10001.
set -eu
ROLE="${1:-api}"
mkdir -p /app/data
chown -R argus:argus /app/data
export UVICORN_PORT="${PORT:-8080}"
cd /app
if [ "$ROLE" = "api" ]; then
  # Wait for Postgres/Redis, apply migrations with the owner URL, (re)grant the restricted runtime role.
  setpriv --reuid=10001 --regid=10001 --clear-groups python /usr/local/bin/railway-db-setup.py migrate
else
  # Workers wait until the api has migrated the schema and the runtime role can read it.
  setpriv --reuid=10001 --regid=10001 --clear-groups python /usr/local/bin/railway-db-setup.py wait
fi
# The schema-owner URL is only for migrations; the app runs with the restricted runtime role.
unset ALEMBIC_DATABASE_URL
exec setpriv --reuid=10001 --regid=10001 --clear-groups /usr/local/bin/argus-entrypoint "$@"
