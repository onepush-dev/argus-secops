# Redis 7 job queue for Argus: append-only persistence on /data, noeviction (queue data must not be evicted),
# password from REDIS_PASSWORD. Baked because Railway templates only keep references and secrets.
FROM redis:7.4-alpine
LABEL org.opencontainers.image.source="https://github.com/onepush-dev/argus-secops"
CMD ["sh", "-c", "exec redis-server --appendonly yes --appendfsync everysec --maxmemory ${REDIS_MAXMEMORY:-256mb} --maxmemory-policy noeviction --save '' --bind '* -::*' --protected-mode no ${REDIS_PASSWORD:+--requirepass \"$REDIS_PASSWORD\"}"]
