from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
PAGES_DIR = BASE_DIR / "github_pages"
HTML_FILE = DIST_DIR / "parole-infinito.html"
API_CONFIG_FILE = DIST_DIR / "api-config.js"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepara un pacchetto statico per GitHub Pages a partire dalla build locale."
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Non esegue build.py prima dell'export",
    )
    parser.add_argument(
        "--api-base",
        default="",
        help="Valore da scrivere in api-config.js, ad esempio https://api.example.com",
    )
    parser.add_argument(
        "--cname",
        default="",
        help="Se valorizzato, crea il file CNAME nel pacchetto Pages",
    )
    return parser.parse_args()


def normalize_api_base_url(value: str) -> str:
    return value.strip().rstrip("/")


def build_project() -> None:
    subprocess.run([sys.executable, "build.py"], cwd=BASE_DIR, check=True)


def write_api_config(path: Path, api_base: str) -> None:
    normalized = normalize_api_base_url(api_base)
    path.write_text(
        (
            "// Configurazione frontend per GitHub Pages.\n"
            "// Imposta l'URL base delle API remote; lascia stringa vuota per stesso host.\n"
            f'window.WOORDLE_API_BASE_URL = "{normalized}";\n'
        ),
        encoding="utf-8",
    )


def prepare_pages_dir() -> None:
    if PAGES_DIR.exists():
        shutil.rmtree(PAGES_DIR)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)


def export_pages_package(api_base: str, cname: str) -> None:
    if not HTML_FILE.exists():
        raise SystemExit("Build non trovata. Esegui prima build.py oppure non usare --skip-build.")

    prepare_pages_dir()

    html = HTML_FILE.read_text(encoding="utf-8")
    (PAGES_DIR / "index.html").write_text(html, encoding="utf-8")
    (PAGES_DIR / "parole-infinito.html").write_text(html, encoding="utf-8")
    (PAGES_DIR / "404.html").write_text(html, encoding="utf-8")
    write_api_config(PAGES_DIR / "api-config.js", api_base)
    (PAGES_DIR / ".nojekyll").write_text("", encoding="utf-8")

    if cname.strip():
        (PAGES_DIR / "CNAME").write_text(cname.strip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    if not args.skip_build:
        build_project()

    export_pages_package(args.api_base, args.cname)

    print(f"Pacchetto GitHub Pages pronto in {PAGES_DIR}")
    print(f"File principali: {PAGES_DIR / 'index.html'} e {PAGES_DIR / 'api-config.js'}")


if __name__ == "__main__":
    main()
