#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${DUCKDNS_ENV_FILE:-$BASE_DIR/duckdns.env}"
LOG_FILE="${DUCKDNS_LOG_FILE:-$BASE_DIR/duckdns.log}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "File config non trovato: $ENV_FILE" >&2
  echo "Copia duckdns.env.example in duckdns.env e inserisci dominio/token." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

: "${DUCKDNS_DOMAIN:?DUCKDNS_DOMAIN mancante}"
: "${DUCKDNS_TOKEN:?DUCKDNS_TOKEN mancante}"

DUCKDNS_IP="${DUCKDNS_IP:-}"
UPDATE_URL="https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=${DUCKDNS_IP}"

response="$(curl -fsS "$UPDATE_URL")"
timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "$timestamp $response" >> "$LOG_FILE"

if [[ "$response" != "OK" ]]; then
  echo "DuckDNS update fallito: $response" >&2
  exit 1
fi

echo "DuckDNS aggiornato: https://${DUCKDNS_DOMAIN}.duckdns.org"
