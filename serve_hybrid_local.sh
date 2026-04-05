#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_PORT="4173"
BACKEND_PORT="8014"
RUN_BUILD="1"

usage() {
  cat <<'EOF'
Uso:
  ./serve_hybrid_local.sh [--frontend-port PORTA] [--backend-port PORTA] [--no-build]

Descrizione:
  Avvia una simulazione locale della futura architettura ibrida:
  - frontend statico servito da una origine separata
  - backend API su una seconda origine con CORS esplicito

URL frontend stampato a video:
  http://127.0.0.1:<frontend-port>/parole-infinito.html?api_base=http%3A%2F%2F127.0.0.1%3A<backend-port>
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --frontend-port)
      FRONTEND_PORT="${2:-}"
      shift 2
      ;;
    --backend-port)
      BACKEND_PORT="${2:-}"
      shift 2
      ;;
    --no-build)
      RUN_BUILD="0"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Argomento non riconosciuto: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! [[ "$FRONTEND_PORT" =~ ^[0-9]+$ && "$BACKEND_PORT" =~ ^[0-9]+$ ]]; then
  echo "Le porte devono essere numeriche." >&2
  exit 1
fi

cd "$BASE_DIR"

if [[ "$RUN_BUILD" == "1" ]]; then
  python3 build.py
fi

FRONTEND_ORIGIN="http://127.0.0.1:${FRONTEND_PORT}"
BACKEND_ORIGIN="http://127.0.0.1:${BACKEND_PORT}"
ENCODED_BACKEND_ORIGIN="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$BACKEND_ORIGIN")"
FRONTEND_URL="${FRONTEND_ORIGIN}/parole-infinito.html?api_base=${ENCODED_BACKEND_ORIGIN}"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  for pid in "$BACKEND_PID" "$FRONTEND_PID"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      wait "$pid" >/dev/null 2>&1 || true
    fi
  done
}

trap cleanup EXIT INT TERM

python3 -u serve_local.py \
  --host 127.0.0.1 \
  --port "$BACKEND_PORT" \
  --allow-origin "$FRONTEND_ORIGIN" \
  --log-http &
BACKEND_PID="$!"

python3 -m http.server "$FRONTEND_PORT" --bind 127.0.0.1 -d dist &
FRONTEND_PID="$!"

echo "Frontend statico: $FRONTEND_URL"
echo "Backend API: ${BACKEND_ORIGIN}/api/attempt"
echo "Premi Ctrl+C per fermare entrambi i server."

wait "$BACKEND_PID" "$FRONTEND_PID"
