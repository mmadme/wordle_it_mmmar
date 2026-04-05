#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$BASE_DIR/data"
PORT="8015"
HOST="0.0.0.0"
PUBLIC_HOST=""
RUN_BUILD="1"

usage() {
  cat <<'EOF'
Uso:
  ./share_public.sh [--port PORTA] [--host HOST] [--public-host IP_O_DOMINIO] [--no-build]

Descrizione:
  Rigenera il progetto e avvia il server HTTP in ascolto pubblico,
  senza usare cloudflared o altri tunnel.

Esempi:
  ./share_public.sh
  ./share_public.sh --port 8010
  ./share_public.sh --public-host 129.153.12.34
  ./share_public.sh --public-host gioco.example.com
  ./share_public.sh --no-build
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --host)
      HOST="${2:-}"
      shift 2
      ;;
    --public-host)
      PUBLIC_HOST="${2:-}"
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

if [[ -z "$PORT" || ! "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Porta non valida: $PORT" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 non trovato. Installa Python 3 e riprova." >&2
  exit 1
fi

mkdir -p "$DATA_DIR"

SERVER_OUT="$DATA_DIR/serve_public.out.log"
SERVER_ERR="$DATA_DIR/serve_public.err.log"

cd "$BASE_DIR"

if [[ "$RUN_BUILD" == "1" ]]; then
  python3 build.py
fi

echo "Avvio server pubblico su $HOST:$PORT"
echo "Log stdout: $SERVER_OUT"
echo "Log stderr: $SERVER_ERR"

if [[ -n "$PUBLIC_HOST" ]]; then
  echo "Link da condividere: http://$PUBLIC_HOST:$PORT/parole-infinito.html"
else
  echo "Link da condividere: http://IP_PUBBLICO_DELLA_VPS:$PORT/parole-infinito.html"
fi

echo "Ricorda di aprire la porta $PORT sia in Oracle Cloud sia nel firewall di Ubuntu."
echo "Premi Ctrl+C per fermare il server."

exec python3 -u serve_local.py --host "$HOST" --port "$PORT" 2>"$SERVER_ERR" | tee "$SERVER_OUT"
