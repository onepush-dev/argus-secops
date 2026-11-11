# Argus SecOps on Railway

[Argus](https://github.com/thomasunise/argus) is an open-source (MIT) agentic security operations platform: detections, AI investigation agents, an action broker with approvals and rollback, an AI gateway, and a signed audit chain. Deploy it on Railway with one click.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/Xu-AlK)

Community packaging of upstream commit `6c057e1` (image built unmodified from the upstream Dockerfile); not affiliated with the upstream authors. Not related to other projects named "Argus".

## What you get
- `argus-api` (FastAPI, public HTTPS, health `/ready`) and `argus-worker` (Redis queue worker), both from one image.
- `argus-db` (Postgres 16) and `argus-redis` (Redis 7, append-only, `noeviction`), private networking only, each with a volume.
- Production mode as upstream intends: HTTPS-only cookies, TOTP required, signed audit chain (JSONL mirror on the `/app/data` volume), encryption at rest, and a **restricted non-owner Postgres runtime role** (row-level security is enforced; migrations run with the owner role at api start).
- All secrets generated per deploy (`ADMIN_PASSWORD`, `SESSION_SECRET`, `DATA_ENCRYPTION_KEY`, `AUDIT_SIGNING_KEY`, database and Redis passwords). No inputs needed.

## First use
1. Open the `argus-api` URL. Sign in as `admin@argus.local` with `ADMIN_PASSWORD` from the `argus-api` Variables tab.
2. Enrol an authenticator app when asked (TOTP is required in production), then change the password.
3. AI agents are off (`AI_PROVIDER=none`). To enable them, add `AI_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` (or `openai` + `OPENAI_API_KEY`) to **both** `argus-api` and `argus-worker`.

Keep `DATA_ENCRYPTION_KEY` and `AUDIT_SIGNING_KEY` safe: changing them makes encrypted columns and the audit chain unreadable.

## Layout
- `app/` wrapper image (start script, migration + runtime-role setup), `worker/` worker tag, `db/` and `redis/` images with baked defaults.
- `.github/workflows/publish-ghcr.yml` builds everything to `ghcr.io/onepush-dev/argus-secops*`.
