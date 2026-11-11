# Argus queue worker: same image as the api, default command `worker`, no HTTP healthcheck.
ARG BASE=ghcr.io/onepush-dev/argus-secops:6c057e1
FROM ${BASE}
LABEL org.opencontainers.image.source="https://github.com/onepush-dev/argus-secops"
HEALTHCHECK NONE
CMD ["worker"]
