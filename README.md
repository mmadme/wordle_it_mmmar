# Parole Infinito — woordle_new_github

Clone italiano di Wordle con export statico per GitHub Pages.

## Cosa fa il gioco

Parole Infinito è un gioco di indovinare parole italiane di 5 lettere in 6 tentativi, ispirato a Wordle.

Due modalità:

- **Infinita (∞)**: partite illimitate con parola casuale estratta in modo pesato per difficoltà
- **Giornaliera (24H)**: una sola parola al giorno, uguale per tutti

Feedback per ogni tentativo:
- Verde: lettera corretta nella posizione giusta
- Giallo: lettera presente ma nella posizione sbagliata
- Grigio: lettera non presente nella parola

Il gioco resta giocabile interamente nel browser; il pacchetto statico pubblicato non contiene URL sensibili hardcoded nell'HTML.

## Struttura del progetto

```
src/
  template_parole.html      template sorgente del gioco (2300+ righe)

dist/                       output del build (non versionato)
  parole-infinito.html      gioco finale giocabile
  parole_soluzioni.txt      1319 parole soluzione
  parole_tentativi.txt      7804 parole accettate come tentativo
  api-config.js             configurazione ambiente generata in build

github_pages/               pacchetto statico per GitHub Pages (non versionato)
  index.html
  parole-infinito.html
  404.html
  api-config.js             configurazione ambiente iniettata dalla CI
  .nojekyll

data/
  vocabolario.json          override editoriali versionati del vocabolario
  definizioni.json          definizioni brevi delle parole soluzione, iniettate nel frontend

.github/workflows/
  github-pages.yml          CI/CD: build e deploy automatico su GitHub Pages

docs/
  CHANGELOG.md              storia delle modifiche
  patch.md                  roadmap e diario delle fasi di lavoro
  playtest_report.md        report analitico del playtest
  github_repo_setup.md      setup iniziale repo GitHub
  build_log.md              output dell'ultima build
  build_history.md          storico build
  stato_progetto.md         fotografia iniziale del progetto

build.py                    generatore principale: fetch dizionari, override editoriali, definizioni, classificazione difficoltà, build HTML
build_github_pages.py       esporta il pacchetto GitHub Pages da dist/
report_playtest.py          genera report CSV e markdown dal database
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
```

## Build e deploy su GitHub Pages

```bash
# Genera il pacchetto statico per Pages
python3 build_github_pages.py --api-base https://backend.example.com
```

Il workflow `.github/workflows/github-pages.yml` automatizza questo passaggio a ogni push su `main`.
Legge la configurazione ambiente dalla secret `PAGES_API_BASE_URL` del repository.

Setup iniziale:

1. Crea la repository su GitHub e fai push di `main`
2. `Settings` → `Secrets and variables` → `Actions` → crea `PAGES_API_BASE_URL`
3. `Settings` → `Pages` → `Source`: `GitHub Actions`

Guida completa: `docs/github_repo_setup.md`

## File non versionati

`.gitignore` esclude:

- `data/*.db` e `data/*.csv` (database e export locali)
- `data/*.log` (log runtime)
- `.env` e `.env.*` (configurazioni locali)
- `dist/` e `github_pages/` (artefatti di build)
- `__pycache__/`

## Documentazione

- [Changelog](docs/CHANGELOG.md)
- [Patch Plan](docs/patch.md)
- [Report Playtest](docs/playtest_report.md)
- [Activity DB - Last 2 Weeks](docs/db_activity_last_2_weeks_2026-04-17.md)
- [Activity DB - Executive Summary](docs/db_activity_manager_summary_2026-04-17.md)
- [Setup repo GitHub](docs/github_repo_setup.md)

## Nota sulla struttura del repo

Questa cartella (`woordle_new_github`) è separata da `woordle_new` per evitare regressioni durante la migrazione all'architettura ibrida. Il lavoro sulla variante GitHub Pages + backend VPS si svolge interamente qui.
