from __future__ import annotations

import argparse
import http.server
import json
import socket
import sqlite3
import webbrowser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
DATA_DIR = BASE_DIR / "data"
INDEX_FILE = DIST_DIR / "parole-infinito.html"
DB_FILE = DATA_DIR / "playtest.db"


class ReusableThreadingHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def get_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve il gioco Parole Infinito dalla cartella dist/ e registra i playtest in SQLite."
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host su cui ascoltare")
    parser.add_argument("--port", type=int, default=8015, help="Porta HTTP")
    parser.add_argument(
        "--allow-origin",
        action="append",
        dest="allow_origins",
        help="Origine consentita per le API. Ripetibile o separata da virgole. Default: *",
    )
    parser.add_argument(
        "--log-http",
        action="store_true",
        help="Mostra log HTTP minimi per debug",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Apre automaticamente il browser locale",
    )
    return parser.parse_args()


def normalize_allowed_origins(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return ("*",)

    origins: list[str] = []
    for value in values:
        for item in value.split(","):
            origin = item.strip().rstrip("/")
            if origin:
                origins.append(origin)

    if not origins:
        return ("*",)

    # Preserve order while removing duplicates.
    return tuple(dict.fromkeys(origins))


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS playtest_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              event_type TEXT NOT NULL,
              session_id TEXT,
              client_id TEXT,
              mode TEXT,
              challenge_id TEXT,
              game_no INTEGER,
              daily_no INTEGER,
              attempt_no INTEGER,
              guess TEXT,
              result_pattern TEXT,
              solution TEXT,
              won INTEGER,
              finished INTEGER,
              remote_ip TEXT,
              user_agent TEXT,
              meta_json TEXT
            )
            """
        )


class PlaytestHandler(http.server.SimpleHTTPRequestHandler):
    allowed_origins: tuple[str, ...] = ("*",)
    log_http = False

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def is_api_request(self) -> bool:
        return self.path.startswith("/api/")

    def cors_origin(self) -> str | None:
        if "*" in self.allowed_origins:
            return "*"

        origin = self.headers.get("Origin", "").strip().rstrip("/")
        if origin and origin in self.allowed_origins:
            return origin
        return None

    def send_cors_headers(self) -> None:
        origin = self.cors_origin()
        if origin is None:
            return
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if origin != "*":
            self.send_header("Vary", "Origin")

    def send_api_json(self, status: int, payload: dict[str, object]) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        if self.is_api_request():
            self.send_cors_headers()
        super().end_headers()

    def do_OPTIONS(self) -> None:
        if self.is_api_request():
            self.send_response(204)
            self.end_headers()
            return
        super().do_OPTIONS()

    def do_POST(self) -> None:
        if self.path == "/api/attempt":
            self.handle_attempt()
            return
        if self.is_api_request():
            self.send_api_json(404, {"error": "Endpoint non trovato"})
            return
        self.send_error(404, "Endpoint non trovato")

    def log_message(self, format: str, *args) -> None:
        if not self.log_http:
            return
        message = format % args
        print(f"[{self.log_date_time_string()}] {self.client_address[0]} {self.command} {self.path} -> {message}")

    def handle_attempt(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8") or "{}")
            if not isinstance(payload, dict):
                raise ValueError("Payload non valido")
        except Exception:
            self.send_api_json(400, {"error": "Payload non valido"})
            return

        remote_ip = self.headers.get("CF-Connecting-IP") or self.client_address[0]
        user_agent = self.headers.get("User-Agent", "")
        meta_json = json.dumps(payload, ensure_ascii=False)

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                """
                INSERT INTO playtest_events (
                  event_type, session_id, client_id, mode, challenge_id, game_no,
                  daily_no, attempt_no, guess, result_pattern, solution, won,
                  finished, remote_ip, user_agent, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.get("event_type"),
                    payload.get("session_id"),
                    payload.get("client_id"),
                    payload.get("mode"),
                    payload.get("challenge_id"),
                    payload.get("game_no"),
                    payload.get("daily_no"),
                    payload.get("attempt_no"),
                    payload.get("guess"),
                    payload.get("result_pattern"),
                    payload.get("solution"),
                    payload.get("won"),
                    payload.get("finished"),
                    remote_ip,
                    user_agent,
                    meta_json,
                ),
            )

        self.send_response(204)
        self.end_headers()


def main() -> None:
    args = parse_args()
    if not INDEX_FILE.exists():
        raise SystemExit("File dist/parole-infinito.html non trovato. Esegui prima: python build.py")

    init_db()
    PlaytestHandler.allowed_origins = normalize_allowed_origins(args.allow_origins)
    PlaytestHandler.log_http = args.log_http

    with ReusableThreadingHTTPServer((args.host, args.port), PlaytestHandler) as httpd:
        local_ip = get_local_ip()
        local_url = f"http://127.0.0.1:{args.port}/parole-infinito.html"
        lan_url = f"http://{local_ip}:{args.port}/parole-infinito.html"

        print("Server playtest avviato.")
        print(f"Cartella servita: {DIST_DIR}")
        print(f"Database log: {DB_FILE}")
        print(f"Locale: {local_url}")
        print(f"Rete locale: {lan_url}")
        print(f"Origini API consentite: {', '.join(PlaytestHandler.allowed_origins)}")
        print(f"Log HTTP: {'attivi' if PlaytestHandler.log_http else 'disattivi'}")
        print("Per fermarlo premi Ctrl+C.")

        if args.open:
            webbrowser.open(local_url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer fermato.")


if __name__ == "__main__":
    main()
