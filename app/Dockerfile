# Argus (thomasunise/argus, MIT) on Railway. FROM the upstream image built unmodified from the pinned commit
# (see .github/workflows/publish-ghcr.yml). This layer only adds production defaults and a start wrapper that:
#   - prepares the /app/data volume (Railway volumes are root-owned) and drops to the image's uid 10001
#   - waits for Postgres and Redis, then (api role) runs Alembic migrations as the schema owner and
#     provisions the restricted non-owner runtime role that upstream requires in production (docs/TENANT-ISOLATION.md)
ARG BASE=ghcr.io/onepush-dev/argus-secops-base:6c057e1
FROM ${BASE}
LABEL org.opencontainers.image.source="https://github.com/onepush-dev/argus-secops" \
      org.opencontainers.image.licenses="MIT"
USER root
RUN apt-get update && apt-get install -y --no-install-recommends util-linux && rm -rf /var/lib/apt/lists/*
ENV APP_ENV=production \
    COOKIE_SECURE=true \
    LOG_JSON=true \
    TOTP_REQUIRED=true \
    DB_AUTO_CREATE=false \
    RUN_MIGRATIONS=false \
    WORKERS_INPROCESS=false \
    FORWARDED_ALLOW_IPS=* \
    AUDIT_JSONL_PATH=/app/data/audit.jsonl \
    SCAN_ROOT=/app/targets \
    RETENTION_ENABLED=true \
    BACKUP_ENABLED=false \
    AI_PROVIDER=none \
    ADMIN_EMAIL=admin@argus.local \
    ARGUS_RUNTIME_DB_USER=argus_runtime
COPY railway-start.sh railway-db-setup.py /usr/local/bin/
RUN chmod 0755 /usr/local/bin/railway-start.sh
EXPOSE 8080
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/railway-start.sh"]
CMD ["api"]
