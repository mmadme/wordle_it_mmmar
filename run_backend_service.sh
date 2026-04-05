#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${WOORDLE_BACKEND_ENV_FILE:-$BASE_DIR/deploy/backend.env}"

BACKEND_HOST="0.0.0.0"
BACKEND_PORT="8015"
BACKEND_ALLOW_ORIGINS="*"
BACKEND_LOG_HTTP="0"
BACKEND_BUILD_ON_START="0"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

cd "$BASE_DIR"
mkdir -p data

if [[ "${BACKEND_BUILD_ON_START}" == "1" ]]; then
  python3 build.py
fi

args=(
  python3
  -u
  serve_local.py
  --host "$BACKEND_HOST"
  --port "$BACKEND_PORT"
)

if [[ -n "${BACKEND_ALLOW_ORIGINS}" ]]; then
  args+=(--allow-origin "$BACKEND_ALLOW_ORIGINS")
fi

if [[ "${BACKEND_LOG_HTTP}" == "1" ]]; then
  args+=(--log-http)
fi

exec "${args[@]}"
