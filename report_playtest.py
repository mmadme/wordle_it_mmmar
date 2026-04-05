from __future__ import annotations

import csv
import sqlite3
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"
DB_FILE = DATA_DIR / "playtest.db"
CSV_FILE = DATA_DIR / "playtest_events.csv"
REPORT_FILE = DOCS_DIR / "playtest_report.md"


def fetch_rows() -> list[sqlite3.Row]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(
            """
            SELECT id, created_at, event_type, session_id, client_id, mode, challenge_id,
                   game_no, daily_no, attempt_no, guess, result_pattern, solution,
                   won, finished, remote_ip, user_agent
            FROM playtest_events
            ORDER BY id ASC
            """
        ).fetchall()
    finally:
        conn.close()


def write_csv(rows: list[sqlite3.Row]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_FILE.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(rows[0].keys() if rows else [
            "id", "created_at", "event_type", "session_id", "client_id", "mode",
            "challenge_id", "game_no", "daily_no", "attempt_no", "guess",
            "result_pattern", "solution", "won", "finished", "remote_ip", "user_agent"
        ])
        for row in rows:
            writer.writerow([row[key] for key in row.keys()])


def build_report(rows: list[sqlite3.Row]) -> str:
    accepted = [r for r in rows if r["event_type"] == "accepted_guess"]
    rejected = [r for r in rows if r["event_type"] == "rejected_guess"]
    ended = [r for r in rows if r["event_type"] == "game_end"]
    won_games = [r for r in ended if r["won"] == 1]
    lost_games = [r for r in ended if r["won"] == 0]

    solutions = Counter(r["solution"] for r in ended if r["solution"])
    guesses = Counter(r["guess"] for r in accepted if r["guess"])
    rejected_guesses = Counter(r["guess"] for r in rejected if r["guess"])
    lost_solutions = Counter(r["solution"] for r in lost_games if r["solution"])
    ips = Counter(r["remote_ip"] for r in rows if r["remote_ip"])
    avg_attempts_won = (
        sum(r["attempt_no"] or 0 for r in won_games) / len(won_games)
        if won_games else 0
    )

    lines = [
        "# Report Playtest",
        "",
        f"- Eventi totali: `{len(rows)}`",
        f"- Tentativi accettati: `{len(accepted)}`",
        f"- Tentativi rifiutati: `{len(rejected)}`",
        f"- Partite concluse: `{len(ended)}`",
        f"- Partite vinte: `{len(won_games)}`",
        f"- Partite perse: `{len(lost_games)}`",
        f"- Media tentativi nelle vittorie: `{avg_attempts_won:.2f}`",
        "",
        "## Soluzioni viste",
        "",
    ]

    if solutions:
        for word, count in solutions.most_common():
            lines.append(f"- `{word}`: {count}")
    else:
        lines.append("- Nessuna soluzione registrata")

    lines += ["", "## Soluzioni perse", ""]
    if lost_solutions:
        for word, count in lost_solutions.most_common(15):
            lines.append(f"- `{word}`: {count}")
    else:
        lines.append("- Nessuna partita persa registrata")

    lines += ["", "## Guess più usati", ""]
    if guesses:
        for word, count in guesses.most_common(15):
            lines.append(f"- `{word}`: {count}")
    else:
        lines.append("- Nessun guess registrato")

    lines += ["", "## Guess rifiutati", ""]
    if rejected_guesses:
        for word, count in rejected_guesses.most_common(15):
            lines.append(f"- `{word}`: {count}")
    else:
        lines.append("- Nessun guess rifiutato")

    lines += ["", "## IP osservati", ""]
    if ips:
        for ip, count in ips.most_common():
            lines.append(f"- `{ip}`: {count}")
    else:
        lines.append("- Nessun IP registrato")

    lines += ["", "## Ultimi eventi", ""]
    for row in rows[-20:]:
        lines.append(
            f"- `{row['created_at']}` | `{row['event_type']}` | mode=`{row['mode']}` | "
            f"guess=`{row['guess'] or '-'}` | solution=`{row['solution'] or '-'}` | "
            f"attempt=`{row['attempt_no'] or '-'}` | ip=`{row['remote_ip'] or '-'}`"
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    if not DB_FILE.exists():
        raise SystemExit("Database non trovato. Avvia prima il server di playtest.")
    rows = fetch_rows()
    write_csv(rows)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(build_report(rows), encoding="utf-8")
    print(f"CSV scritto in {CSV_FILE}")
    print(f"Report scritto in {REPORT_FILE}")


if __name__ == "__main__":
    main()
