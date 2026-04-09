# Diario del Progetto — Parole Infinito

## Obiettivo

Creare un clone italiano di Wordle chiamato **Parole Infinito**, giocabile nel browser, con:

- due modalità (infinita e giornaliera)
- vocabolario curato di parole italiane classificate per difficoltà
- sistema di playtest con logging su SQLite per analizzare il comportamento dei giocatori
- architettura finale ibrida: frontend statico su GitHub Pages, backend Python su VPS Ubuntu

Il gioco nasce come strumento di gioco personale e di test, poi evolve verso un'architettura distribuita e un flusso di deploy automatizzato.

---

## Fonti usate

### Vocabolario
- **[pietroppeter/wordle-it](https://github.com/pietroppeter/wordle-it)** su GitHub: dizionari di parole italiane a 5 lettere usati come base per soluzioni e tentativi. Scaricati a ogni build tramite `urllib`.

### Ispirazione di gioco
- **Wordle** (originale NYT) per la meccanica base: 5 lettere, 6 tentativi, feedback colori.
- **Paroliere**, **Wordle.it** e varianti italiane esistenti per capire quali vocaboli funzionano nel contesto italiano.

### Stack tecnico
- **Python 3** per backend, build e utility
- **SQLite** per il database di logging (integrato in Python, zero dipendenze esterne)
- **GitHub Actions** per il CI/CD del frontend
- **GitHub Pages** per l'hosting statico
- **Caddy** per il reverse proxy HTTPS con Let's Encrypt automatico
- **systemd** per la gestione del servizio backend sulla VPS
- **DuckDNS** per un hostname stabile gratuito per il backend

---

## Logica del progetto

### Il gioco (frontend)

Il frontend è un singolo file HTML autocontenuto generato da `build.py` a partire dal template `src/template_parole.html`. Tutta la logica di gioco è in JavaScript inline.

Flusso di una partita:
1. Il giocatore carica la pagina → il frontend determina la modalità (daily o infinita)
2. In modalità daily: contatta `GET /api/daily` sul backend per ottenere il `challenge_id` del giorno (timezone Roma) e seleziona la parola in modo deterministico
3. In modalità infinita: estrae una parola casuale dalle liste vocabolario con pesi per difficoltà
4. Il giocatore tenta una parola → il frontend verifica che esista nel dizionario tentativi, calcola il feedback (verde/giallo/grigio), invia `POST /api/attempt` al backend per il logging
5. Al termine (vittoria o sconfitta) viene mostrata la modale finale con statistiche e bottone condividi

Stato di gioco salvato in `localStorage` per mantenere la partita tra i refresh.

### Il vocabolario (build.py)

La build scarica i dizionari da GitHub e li processa in più fasi:

1. **Validazione base**: 5 lettere, alfabeto italiano, almeno una vocale, max 3 consonanti consecutive
2. **Scrematura soluzioni**: rimozione di forme verbali poco naturali, cluster ambigui, parole tecniche/arcaiche, forestierismi non integrati
3. **Classificazione difficoltà** su 5 livelli (bassissima → altissima) basata su:
   - rarità delle lettere (frequenza inversa nel corpus)
   - presenza di doppie (+1.2)
   - lettere rare z/q/j/x/k/y/w (+0.8)
   - pochi caratteri unici (<4 unici +0.6)
   - parole comuni nota (-3.0)
   - sovrascritture manuali per parole specifiche
4. **Estrazione pesata** per modalità: la daily ha più parole medie/alte rispetto all'infinita

### Il backend (serve_local.py)

Server HTTP Python con:
- `GET /api/daily`: restituisce metadati della sfida giornaliera (challenge_id, daily_no, resets_at) calcolati con timezone `Europe/Rome`
- `POST /api/attempt`: registra ogni evento di gioco su SQLite (tipo evento, sessione, IP reale, guess, soluzione, risultato)
- Estrazione IP reale dietro proxy: si fida dei header `X-Forwarded-For`, `X-Real-IP`, `CF-Connecting-IP` solo se il peer diretto è loopback

### Il deploy

```
Developer (locale)
  └── python3 build.py                  # genera dist/
  └── python3 build_github_pages.py     # genera github_pages/
  └── git push main

GitHub Actions (CI)
  └── build_github_pages.py --api-base $PAGES_API_BASE_URL
  └── deploy su GitHub Pages

VPS Ubuntu (sempre attivo)
  └── woordle-backend-test.service (systemd)
      └── run_backend_service.sh
          └── serve_local.py --port 8015
  └── Caddy (porta 443)
      └── reverse_proxy 127.0.0.1:8015
  └── DuckDNS cron (ogni 5 min)
      └── update_duckdns.sh
```

---

## Evoluzione del progetto

### 2026-03-26 — Versione iniziale (woordle_new)

La prima versione funzionante nasce in `woordle_new` (cartella separata). Il progetto parte da zero con:
- `buildv2.py` per generare l'HTML del gioco con vocabolario italiano
- frontend HTML singolo, nessun backend, nessun server
- prime verifiche di UI su desktop e mobile

Decisioni iniziali:
- esclusione di forestierismi non italianizzati (`jeans`, `share`, `shake`, `white`)
- mantenimento di prestiti consolidati (`sport`, `focus`, `virus`, `rebus`)
- rimozione di cluster di parole troppo simili (es. famiglie `detto/tetto/cassa`)

Risultato: 1329 soluzioni, ~7800 tentativi.

### 2026-03-26 — Modalità giornaliera e condivisione

Aggiunte in rapida successione:
- selettore modalità `∞` / `24H` nell'header
- daily deterministica basata sulla data locale del browser
- statistiche separate per modalità infinita e giornaliera
- pulsante **Condividi** con copia griglia emoji negli appunti (stile Par🇮🇹le)

Problema trovato e risolto: il contatore locale saltava a `2` se la prima partita in infinita arrivava dopo aver visto la daily.

### 2026-03-26 — Hosting locale per playtest

Aggiunto `serve_local.py` come server HTTP statico per rendere il gioco accessibile in rete locale senza configurare nulla.

### 2026-03-26 — Tunnel temporaneo Cloudflare

Per il primo playtest remoto: `cloudflared.exe` (asset Windows) usato per esporre temporaneamente il server locale con un URL pubblico temporaneo. Soluzione rapida e usa-e-getta, non pensata per la produzione.

### 2026-03-27 — Logging SQLite

Svolta importante: `serve_local.py` trasformato da server statico puro a server di playtest con database SQLite.

Ogni evento registra:
- tipo: `accepted_guess`, `rejected_guess`, `game_end`
- sessione, IP, user-agent
- tentativo, soluzione, pattern risultato
- modalità (infinita/giornaliera), numero partita

Questo permette di analizzare il comportamento dei giocatori reali e capire quali parole sono troppo facili, troppo difficili, o rifiutate ingiustamente.

### 2026-03-27 — Fix modale finale e encoding

Due bug trovati durante il playtest:
1. La modale finale non si riaprива dopo un refresh → introdotta funzione dedicata al render richiamata anche al ripristino
2. La griglia emoji del popup risultava corrotta negli screenshot dei tester → corretta con stringhe Unicode stabili

### 2026-03-28 — Classificazione difficoltà a 3 livelli e rebalance

Il vocabolario passa da un sistema binario (soluzioni/tentativi) a una classificazione per difficoltà:
- `facili`, `medie`, `difficili`
- estrazione pesata: infinita ~65% facili, 25% medie, 10% difficili

Parole spostate da soluzioni a soli tentativi: `bidet`, `cruna`, `biada`, `bitta`, `sport`, `torba` (troppo oscure o atipiche per una soluzione).

La modalità di default diventa `24H` (giornaliera).

### 2026-03-28 — Report playtest

`report_playtest.py` aggiornato per contare le soluzioni viste sulle partite concluse (non sui guess). Aggiunte statistiche su vittorie/sconfitte, media tentativi, soluzioni perse.

---

### 2026-04-05 — Creazione di woordle_new_github

La cartella `woordle_new_github` nasce come duplicato di `woordle_new` per sperimentare l'architettura ibrida (GitHub Pages + backend VPS) senza rischiare regressioni sul branch attivo.

Punto di partenza: tutto funziona localmente, ma il frontend e il backend sono accoppiati sullo stesso host.

#### Fase 0-1 — API_BASE_URL configurabile

Il template HTML viene modificato per leggere `API_BASE_URL` da una variabile esterna invece di hardcodarlo. Questo è il prerequisito per separare frontend e backend su origini diverse.

#### Fase 2 — CORS e errori API

`serve_local.py` aggiornato con:
- `--allow-origin` per configurare le origini consentite
- `--log-http` per debug
- gestione CORS centralizzata su tutte le risposte (`OPTIONS 204`, `400`, `404`)
- errori API in formato JSON coerente

Test: `OPTIONS /api/attempt` con origine esplicita, scrittura reale su SQLite con sessione `phase2-test`.

#### Fase 3 — Hybrid local test

Aggiunto `serve_hybrid_local.sh` per simulare l'architettura finale in locale: frontend statico su porta 4173, backend API su porta 8014 su origini separate. Questo permette di testare CORS prima del deploy reale.

`api-config.js` letto anche da query string e `localStorage` per flessibilità nei test.

#### Fase 4 — build_github_pages.py

Nuovo script per esportare un pacchetto statico ripetibile in `github_pages/`:
- copia `parole-infinito.html` come `index.html` e come pagina principale
- genera `404.html` per il fallback GitHub Pages
- inietta `api-config.js` con l'URL backend passato come argomento
- aggiunge `.nojekyll` per evitare che GitHub processi il sito con Jekyll

`build.py` aggiornato per generare anche `dist/api-config.js` locale.

#### Fase 5 — DuckDNS

`duckdns/update_duckdns.sh` per aggiornare automaticamente l'hostname DuckDNS con l'IP pubblico della VPS. Cron job attivo ogni 5 minuti.

Il dominio DuckDNS (`sborraparle.duckdns.org`) diventa il riferimento stabile per il backend.

#### Fase 6 — systemd

Backend promosso a servizio di sistema:
- `run_backend_service.sh` come wrapper di avvio (legge file `.env`, supporta variabili d'ambiente)
- unit file `woordle-backend-test.service` (systemd) con restart automatico
- porta definitiva `8015` per la variante GitHub

Servizio attivato: `woordle-backend-test.service` → `active` + `enabled`.

#### Fase 7 — HTTPS con Caddy

Caddy installato sulla VPS come reverse proxy:
- `Caddyfile.example` con configurazione minima
- HTTPS automatico via Let's Encrypt
- redirect HTTP→HTTPS (308)
- forward verso `127.0.0.1:8015`

Blocco incontrato: l'emissione del certificato TLS dipende dalla raggiungibilità pubblica delle porte 80/443 (Oracle Cloud security group). Risolto verificando le regole firewall.

#### Workflow GitHub Actions

`.github/workflows/github-pages.yml` aggiunto:
- trigger: push su `main` o dispatch manuale
- verifica sintassi Python
- esegue `build_github_pages.py --api-base ${{ secrets.PAGES_API_BASE_URL }}`
- pubblica `github_pages/` su GitHub Pages

`PAGES_API_BASE_URL` salvato come secret del repository (non variabile) per non esporre l'endpoint backend nei log pubblici.

---

### 2026-04-06 — Daily sincronizzata via backend

Fino a questo punto la daily era calcolata sul client usando la data locale del browser. Questo creava incoerenze tra fusi orari diversi.

Soluzione:
- `serve_local.py` esteso con `GET /api/daily` che restituisce `challenge_id`, `daily_no`, `day_key`, `timezone`, `resets_at` con timezone `Europe/Rome`
- il frontend usa il backend come fonte autorevole della daily
- fallback locale mantenuto se il backend non risponde

Allo stesso tempo: fix IP reale dietro proxy. Il backend estraeva sempre `127.0.0.1` perché Caddy faceva da proxy. Soluzione: se il peer diretto è loopback, il backend legge l'IP reale dagli header (`X-Forwarded-For`, `X-Real-IP`, `CF-Connecting-IP`, `Forwarded`). Questo permette un tracciamento accurato degli IP nei playtest.

### 2026-04-06 — Fix blank UI su backend lento

Bug rilevato: se il backend è lento a rispondere, il frontend mostrava una schermata bianca in attesa della daily.

Fix: il frontend mostra l'interfaccia di gioco immediatamente e aggiorna i metadati della daily quando arriva la risposta, senza bloccare il render iniziale.

### 2026-04-06 — Allineamento documentazione

Tutta la documentazione tecnica (`patch.md`, `backend_https_caddy.md`, `backend_service_systemd.md`, `backend_hostname_duckdns.md`, `backend_management.md`, `README.md`) allineata allo stato operativo reale: HTTPS attivo, backend su 8015, daily dal server.

---

## Stato operativo attuale (2026-04-09)

| Componente | Stato |
|------------|-------|
| Backend systemd | attivo su `127.0.0.1:8015` |
| Reverse proxy Caddy | attivo su `443` HTTPS |
| Hostname DuckDNS | `sborraparle.duckdns.org` aggiornato via cron |
| Frontend GitHub Pages | deployato automaticamente via CI |
| Database SQLite | 555 eventi, 85 partite, 79 vinte |

### Metriche playtest

- **Win rate**: 92.9% (79/85)
- **Media tentativi nelle vittorie**: 4.15
- **IP distinti**: 26
- **Apertura più usata**: `sedia` (14 partite)
- **Soluzioni perse**: largo, bitta, bulbo, punge, tonno, emiro
- **Guess rifiutati più tentati**: `froci` (3 tentativi, non nel vocabolario)
- **Parola giornaliera attuale** (2026-04-09): `tosse`

### Vocabolario finale

- 1319 soluzioni (classificate su 5 livelli di difficoltà)
- 7802 parole accettate come tentativo

---

## Decisioni tecniche rilevanti

### Perché un file HTML unico

Il gioco è un singolo HTML autocontenuto per semplicità di deploy: basta copiare un file per avere un gioco funzionante. La separazione frontend/backend riguarda solo il logging e la daily; la logica di gioco gira interamente nel browser.

### Perché SQLite e non un servizio esterno

Zero dipendenze esterne, backup banale (`cp data/playtest.db backup.db`), query SQL dirette per il report. Per un playtest con qualche decina di utenti è più che sufficiente.

### Perché DuckDNS e non un dominio a pagamento

Il progetto è un prototipo/playtest. DuckDNS offre un hostname stabile gratuito con aggiornamento IP automatico. Se il progetto dovesse crescere, si passa a un dominio vero.

### Perché woordle_new_github separato da woordle_new

Per non rompere la versione attiva durante la migrazione all'architettura ibrida. Le due cartelle coesistono finché la variante GitHub Pages non è consolidata.

### Perché la classificazione a 5 livelli e non 3

Passato da 3 livelli (facili/medie/difficili) a 5 (bassissima/bassa/media/alta/altissima) per un controllo più fine sulla distribuzione del vocabolario. La daily può pesare di più le parole medie/alte rispetto all'infinita, rendendo la sfida giornaliera leggermente più impegnativa.

### Perché il frontend non blocca su backend lento

La daily viene mostrata appena il backend risponde, ma il gioco è già usabile prima. Un frontend che aspetta una risposta API prima di renderizzare è una UX pessima su connessioni lente.
