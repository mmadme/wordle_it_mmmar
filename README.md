# Parole Infinito — woordle_new_github

Clone italiano di Wordle con architettura ibrida: frontend statico su GitHub Pages e backend Python + SQLite su VPS Ubuntu.

## Cosa fa il gioco

Parole Infinito è un gioco di indovinare parole italiane di 5 lettere in 6 tentativi, ispirato a Wordle.

Due modalità:

- **Infinita (∞)**: partite illimitate con parola casuale estratta in modo pesato per difficoltà
- **Giornaliera (24H)**: una sola parola al giorno, uguale per tutti, determinata dal backend con timezone `Europe/Rome`

Feedback per ogni tentativo:
- Verde: lettera corretta nella posizione giusta
- Giallo: lettera presente ma nella posizione sbagliata
- Grigio: lettera non presente nella parola

Il gioco funziona interamente nel browser. Il backend è opzionale per la modalità infinita, ma necessario per la daily sincronizzata e per il logging playtest.

## Architettura

```
GitHub Pages (frontend)     https://<user>.github.io/<repo>/
        ↓ CORS
Caddy (reverse proxy)       https://sborraparle.duckdns.org  (443)
        ↓ loopback
Backend Python              http://127.0.0.1:8015
        ↓
SQLite                      data/playtest.db
```

Il frontend legge l'URL del backend da `api-config.js`, generato durante la build. Non c'è nessun URL hardcoded nell'HTML.

## Struttura del progetto

```
src/
  template_parole.html      template sorgente del gioco (2300+ righe)

dist/                       output del build (non versionato)
  parole-infinito.html      gioco finale giocabile
  parole_soluzioni.txt      1319 parole soluzione
  parole_tentativi.txt      7802 parole accettate come tentativo
  api-config.js             URL backend per l'ambiente locale

github_pages/               pacchetto statico per GitHub Pages (non versionato)
  index.html
  parole-infinito.html
  404.html
  api-config.js             URL backend reale (iniettato dalla secret CI)
  .nojekyll

data/
  playtest.db               database SQLite eventi (non versionato)
  playtest_events.csv       export CSV (non versionato)

deploy/
  systemd/                  unit file systemd per il backend
  caddy/Caddyfile.example   reverse proxy HTTPS con Caddy
  backend.env.example       variabili d'ambiente backend
  backend-test.env.example  variabili d'ambiente ambiente di test

duckdns/
  update_duckdns.sh         aggiornamento IP su DuckDNS (cron)
  duckdns.env.example       template configurazione

.github/workflows/
  github-pages.yml          CI/CD: build e deploy automatico su GitHub Pages

docs/
  CHANGELOG.md              storia delle modifiche
  patch.md                  roadmap e diario delle fasi di lavoro
  playtest_report.md        report analitico del playtest
  backend_service_systemd.md  guida systemd
  backend_https_caddy.md    guida HTTPS Caddy
  backend_hostname_duckdns.md  guida DuckDNS
  backend_management.md     guida operativa quotidiana
  github_repo_setup.md      setup iniziale repo GitHub
  build_log.md              output dell'ultima build
  build_history.md          storico build
  stato_progetto.md         fotografia iniziale del progetto

build.py                    generatore principale: fetch dizionari, filtraggio, classificazione difficoltà, build HTML
build_github_pages.py       esporta il pacchetto GitHub Pages da dist/
serve_local.py              backend HTTP + API SQLite
report_playtest.py          genera report CSV e markdown dal database
run_backend_service.sh      wrapper di avvio per systemd
serve_hybrid_local.sh       simula architettura ibrida in locale (frontend 4173, backend 8014)
share_public.sh             avvio rapido backend su VPS
```

## Vocabolario

Il vocabolario viene generato da `build.py` a partire da sorgenti esterne (dizionari wordle-it su GitHub) con un pipeline di filtraggio e classificazione:

**Filtraggio soluzioni:**
- solo parole di 5 lettere con almeno una vocale
- rimosse forme verbali troppo specifiche (passato remoto in -ai/-ii, congiuntivi rari)
- rimossi cluster di parole troppo simili (famiglie con 6+ varianti)
- rimossi forestierismi non integrati
- alcune parole aggiunte manualmente (`froci`, `negra`)

**Classificazione difficoltà** (5 livelli):

| Livello | N. parole | Criteri |
|---------|-----------|---------|
| Bassissima | 405 | parole molto comuni, bassa rarità lettere |
| Bassa | 320 | parole comuni |
| Media | 322 | rarità media |
| Alta | 197 | lettere rare, doppie, pochi caratteri unici |
| Altissima | 75 | rarità estrema + sovrascrittura manuale |

**Pesi estrazione:**

| Modalità | Bassissima | Bassa | Media | Alta | Altissima |
|----------|-----------|-------|-------|------|-----------|
| Infinita | 30% | 25% | 25% | 15% | 5% |
| Giornaliera | 20% | 25% | 30% | 20% | 5% |

**Risultato finale:** 1319 soluzioni, 7802 tentativi accettati.

## Avvio locale

Requisiti: Python 3, connessione internet (per il fetch dei dizionari al primo build).

```bash
# Build del gioco
python3 build.py

# Avvio backend locale (serve dist/ + API SQLite)
python3 serve_local.py --host 127.0.0.1 --port 8015 --open

# Simulazione architettura ibrida (frontend su 4173, backend su 8014)
bash serve_hybrid_local.sh
```

## Build e deploy su GitHub Pages

```bash
# Genera il pacchetto statico con URL backend esplicito
python3 build_github_pages.py --api-base https://<backend-domain>
```

Il workflow `.github/workflows/github-pages.yml` automatizza questo passaggio a ogni push su `main`.
Legge l'URL del backend dalla secret `PAGES_API_BASE_URL` del repository.

Setup iniziale:

1. Crea la repository su GitHub e fai push di `main`
2. `Settings` → `Secrets and variables` → `Actions` → crea `PAGES_API_BASE_URL`
3. `Settings` → `Pages` → `Source`: `GitHub Actions`

Guida completa: `docs/github_repo_setup.md`

## Backend su VPS

Il backend gira come servizio systemd dietro Caddy con HTTPS automatico.

Stack:

- `serve_local.py` in ascolto su `127.0.0.1:8015`
- Caddy in reverse proxy su `443` con certificato Let's Encrypt
- DuckDNS per hostname stabile gratuito

Endpoint API:

- `GET /api/daily` → metadati daily (challenge_id, daily_no, resets_at, timezone)
- `POST /api/attempt` → registra un evento di gioco nel database SQLite

Variabili d'ambiente principali (file `.env` o `/etc/woordle-backend-test.env`):

```
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8015
BACKEND_ALLOW_ORIGINS=https://<frontend-domain>
BACKEND_LOG_HTTP=0
BACKEND_BUILD_ON_START=0
```

Guide operative:

- `docs/backend_service_systemd.md`
- `docs/backend_https_caddy.md`
- `docs/backend_hostname_duckdns.md`
- `docs/backend_management.md`

## Report playtest

```bash
python3 report_playtest.py
```

Genera `data/playtest_events.csv` e aggiorna `docs/playtest_report.md`.

Dati attuali (2026-04-09):

- 555 eventi registrati
- 85 partite concluse, 79 vinte (92.9% win rate)
- 9 IP distinti
- media tentativi nelle vittorie: 4.15
- apertura più usata: `sedia` (14 volte)

## CORS

Con frontend su GitHub Pages (HTTPS) e backend su dominio separato, il CORS è obbligatorio.

```bash
BACKEND_ALLOW_ORIGINS=https://<frontend-domain>
```

Il backend risponde alle preflight `OPTIONS` e aggiunge gli header `Access-Control-Allow-*` automaticamente.

## File non versionati

`.gitignore` esclude:

- `data/playtest.db` e `data/*.csv` (database reali)
- `data/*.log` (log runtime)
- `duckdns/duckdns.env` (token DuckDNS)
- `.env` e `.env.*` (configurazioni locali)
- `dist/` e `github_pages/` (artefatti di build)
- `__pycache__/`

## Documentazione

- [Changelog](docs/CHANGELOG.md)
- [Patch Plan](docs/patch.md)
- [Report Playtest](docs/playtest_report.md)
- [Backend systemd](docs/backend_service_systemd.md)
- [Backend HTTPS Caddy](docs/backend_https_caddy.md)
- [Backend DuckDNS](docs/backend_hostname_duckdns.md)
- [Gestione operativa backend](docs/backend_management.md)
- [Setup repo GitHub](docs/github_repo_setup.md)

## Nota sulla struttura del repo

Questa cartella (`woordle_new_github`) è separata da `woordle_new` per evitare regressioni durante la migrazione all'architettura ibrida. Il lavoro sulla variante GitHub Pages + backend VPS si svolge interamente qui.
