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
  parole_tentativi.txt      7804 parole accettate come tentativo
  api-config.js             URL backend per l'ambiente locale

github_pages/               pacchetto statico per GitHub Pages (non versionato)
  index.html
  parole-infinito.html
  404.html
  api-config.js             URL backend reale (iniettato dalla secret CI)
  .nojekyll

data/
  vocabolario.json          override editoriali versionati del vocabolario
  definizioni.json          definizioni brevi delle parole soluzione, iniettate nel frontend
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

build.py                    generatore principale: fetch dizionari, override editoriali, definizioni, classificazione difficoltà, build HTML
build_github_pages.py       esporta il pacchetto GitHub Pages da dist/
serve_local.py              backend HTTP + API SQLite
report_playtest.py          genera report CSV e markdown dal database
run_backend_service.sh      wrapper di avvio per systemd
serve_hybrid_local.sh       simula architettura ibrida in locale (frontend 4173, backend 8014)
share_public.sh             avvio rapido backend su VPS
```

## Vocabolario

Il vocabolario viene generato da `build.py` a partire da sorgenti esterne (dizionari wordle-it su GitHub) con una pipeline di filtraggio e classificazione.

Le decisioni editoriali non sono piu' hardcoded nel codice Python: oggi sono versionate in `data/vocabolario.json`, che contiene:
- parole sempre comuni da forzare a `bassissima`
- parole da rimuovere dalle `soluzioni` ma lasciare nei `tentativi`
- aggiunte manuali da iniettare nel vocabolario
- override manuali di livello (`altissima`, `alta`, `media`, `bassa`)

Le definizioni brevi delle parole soluzione sono invece in `data/definizioni.json`: durante la build vengono serializzate dentro il blocco JS del template come costante `DEFINIZIONI`, cosi' il frontend puo' mostrarle senza dipendere da chiamate runtime.

**Filtraggio soluzioni:**
- solo parole di 5 lettere con almeno una vocale
- rimosse forme verbali troppo specifiche (passato remoto in -ai/-ii, congiuntivi rari)
- rimossi cluster di parole troppo simili (famiglie con 6+ varianti)
- rimossi forestierismi non integrati
- alcune parole aggiunte manualmente (`froci`, `negra`, `negri`, `negro`, `troia`)

**Classificazione difficoltà** (5 livelli):

| Livello | N. parole | Criteri |
|---------|-----------|---------|
| Bassissima | 348 | parole molto comuni, bassa rarità lettere |
| Bassa | 287 | parole comuni o abbassate da override editoriale |
| Media | 239 | rarità media o override a livello medio |
| Alta | 374 | lettere rare, doppie, pochi caratteri unici o override alto |
| Altissima | 71 | rarità estrema + override manuale |

**Pesi estrazione:**

| Modalità | Bassissima | Bassa | Media | Alta | Altissima |
|----------|-----------|-------|-------|------|-----------|
| Infinita facile | 45% | 30% | 15% | 8% | 2% |
| Infinita media | 25% | 25% | 25% | 18% | 7% |
| Infinita difficile | 5% | 10% | 20% | 35% | 30% |
| Giornaliera | 10% | 20% | 35% | 25% | 10% |

**Risultato finale attuale:** 1319 soluzioni, 7804 tentativi accettati.

Il file `docs/build_log.md` ora logga anche quale `vocabolario.json` e' stato caricato e quanti override contiene per categoria.

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

Nel frontend la daily viene anche ricontrollata quando la scheda torna visibile o riceve `focus`, cosi' una pagina lasciata aperta su mobile non resta bloccata sulla parola del giorno precedente dopo mezzanotte `Europe/Rome`.

Nel popup di fine partita, accanto alla parola soluzione, compare anche un pulsante `ⓘ` quando quella parola ha una voce in `DEFINIZIONI`: il click apre e richiude una definizione breve direttamente nel modal finale.

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

Dati correnti nel DB (2026-04-18, raw):

- 1196 eventi registrati
- ultimo evento: `2026-04-18 10:50:11`
- tabella SQLite unica: `playtest_events`

Per analisi di prodotto piu' utili del report standard ci sono anche:
- `docs/db_activity_last_2_weeks_2026-04-17.md`
- `docs/db_activity_manager_summary_2026-04-17.md`

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
- [Activity DB - Last 2 Weeks](docs/db_activity_last_2_weeks_2026-04-17.md)
- [Activity DB - Executive Summary](docs/db_activity_manager_summary_2026-04-17.md)
- [Backend systemd](docs/backend_service_systemd.md)
- [Backend HTTPS Caddy](docs/backend_https_caddy.md)
- [Backend DuckDNS](docs/backend_hostname_duckdns.md)
- [Gestione operativa backend](docs/backend_management.md)
- [Setup repo GitHub](docs/github_repo_setup.md)

## Nota sulla struttura del repo

Questa cartella (`woordle_new_github`) è separata da `woordle_new` per evitare regressioni durante la migrazione all'architettura ibrida. Il lavoro sulla variante GitHub Pages + backend VPS si svolge interamente qui.
