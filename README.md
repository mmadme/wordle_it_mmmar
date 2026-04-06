# Woordle New GitHub

Versione di lavoro di `Parole Infinito` preparata per l'architettura ibrida del progetto:

- frontend statico pubblicabile su GitHub Pages
- backend Python + SQLite mantenuto sulla VPS Ubuntu
- backend remoto configurabile senza hardcode nel frontend

Questa cartella e' separata dalla versione attiva `woordle_new` per evitare regressioni durante la migrazione.

## Stato attuale

La variante `woordle_new_github` e' gia' pronta su questi punti:

- build locale del gioco con `build.py`
- backend remoto stabile con `serve_local.py`
- deploy persistente del backend con `systemd`
- reverse proxy HTTPS tramite Caddy
- pacchetto statico esportabile per GitHub Pages con `build_github_pages.py`
- configurazione frontend separata in `api-config.js`
- daily sincronizzata tramite backend con timezone ufficiale `Europe/Rome`

Nel flusso attuale la repo rappresenta la variante GitHub Pages + backend VPS gia' allineata a un deploy reale.

I dettagli operativi del backend reale non sono riportati nel README pubblico.

## Struttura del progetto

- `src/template_parole.html`: template sorgente del gioco
- `build.py`: genera `dist/`
- `serve_local.py`: server HTTP/API con logging su SQLite
- `report_playtest.py`: genera report dal database playtest
- `build_github_pages.py`: esporta il pacchetto statico in `github_pages/`
- `run_backend_service.sh`: wrapper di avvio per il servizio backend
- `deploy/systemd/`: unit file `systemd`
- `deploy/caddy/Caddyfile.example`: reverse proxy HTTPS
- `duckdns/`: aggiornamento hostname DuckDNS
- `docs/`: documentazione tecnica e piano patch

## Avvio locale rapido

Requisiti:

- Ubuntu o Linux compatibile
- Python 3

Build:

```bash
python3 build.py
```

Avvio locale:

```bash
python3 serve_local.py --host 127.0.0.1 --port 8015 --open
```

## Generare il frontend per GitHub Pages

Il frontend statico viene esportato in `github_pages/`.

Comando consigliato:

```bash
python3 build_github_pages.py --api-base https://<backend-domain>
```

Output principale:

- `github_pages/index.html`
- `github_pages/parole-infinito.html`
- `github_pages/api-config.js`

## Deploy su GitHub Pages

La repo include un workflow GitHub Actions che:

- esegue la build del frontend
- genera `github_pages/`
- pubblica automaticamente il sito su GitHub Pages
- legge l'URL backend da una secret del repository

Workflow:

- `.github/workflows/github-pages.yml`

Per una nuova copia del progetto o per rifare il setup da zero:

1. crea la repository remota
2. fai push del branch `main`
3. in GitHub vai su `Settings` -> `Secrets and variables` -> `Actions` -> `Secrets`
4. crea `PAGES_API_BASE_URL` con il valore del backend reale
5. in GitHub vai su `Settings` -> `Pages`
6. imposta `Source` su `GitHub Actions`

GitHub Docs ufficiale:

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## CORS e backend remoto

Dato che il frontend e' pensato per girare su GitHub Pages, conviene restringere le origini consentite nel backend invece di lasciare `*`.

Esempio:

```bash
BACKEND_ALLOW_ORIGINS=https://<frontend-domain>
```

Dettagli:

- `docs/backend_service_systemd.md`
- `docs/backend_https_caddy.md`

## File non versionati

Questa repo non deve includere:

- database playtest reali
- log runtime
- file con token o segreti
- URL backend reali dove non sono strettamente necessari

Per questo i file locali sensibili e generati sono esclusi tramite `.gitignore`.

## Documentazione utile

- [Patch Plan](docs/patch.md)
- [Backend DuckDNS](docs/backend_hostname_duckdns.md)
- [Backend systemd](docs/backend_service_systemd.md)
- [Backend HTTPS con Caddy](docs/backend_https_caddy.md)
- [Setup repo GitHub](docs/github_repo_setup.md)
- [Changelog](docs/CHANGELOG.md)

## Nota importante

Questa repo resta separata da `woordle_new` per evitare regressioni sul ramo storico del progetto.

La variante GitHub Pages + backend remoto risulta ormai il riferimento operativo di questa copia; il lavoro residuo riguarda soprattutto manutenzione, monitoraggio e l'eventuale decisione di convergere o meno sul progetto principale.
