# Postgres 16 for Argus. Plain defaults are baked in because Railway templates only keep references and secrets.
FROM postgres:16-alpine
LABEL org.opencontainers.image.source="https://github.com/onepush-dev/argus-secops"
ENV POSTGRES_USER=argus \
    POSTGRES_DB=argus \
    POSTGRES_INITDB_ARGS=--data-checksums \
    PGDATA=/var/lib/postgresql/data/pgdata
