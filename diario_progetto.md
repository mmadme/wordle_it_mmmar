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

### File operativi principali: organizzazione e responsabilita'

Il progetto oggi e' organizzato in pochi file "centrali" che coprono build, runtime, deploy e analisi. La logica non e' sparsa in molti moduli: ogni file ha un ruolo abbastanza netto.

#### Build e vocabolario

- `build.py`
  - e' il generatore principale del progetto
  - scarica i dizionari sorgente da `wordle-it`
  - legge gli override editoriali versionati da `data/vocabolario.json`
  - legge anche `data/definizioni.json` e lo inietta nel frontend come costante JS `DEFINIZIONI`
  - filtra `soluzioni` e `tentativi`
  - classifica le soluzioni in 5 livelli di difficolta'
  - definisce i pesi percentuali usati da daily e infinita
  - inietta vocabolario e costanti JS nel template
  - scrive gli artefatti locali in `dist/` e i log di build in `docs/build_log.md` / `docs/build_history.md`

- `build_github_pages.py`
  - prende la build locale e la trasforma nel pacchetto statico per GitHub Pages
  - genera `github_pages/index.html`, `404.html`, `.nojekyll`
  - scrive `api-config.js` con l'URL del backend passato da CLI o da CI
  - e' il punto di collegamento tra build locale e deploy statico pubblico

#### Frontend di gioco

- `src/template_parole.html`
  - e' il file sorgente principale del frontend
  - contiene struttura HTML, CSS e tutta la logica JS del gioco
  - gestisce modalita' `giornaliera` e `infinita`
  - salva stato, statistiche e difficolta' in `localStorage`
  - applica l'estrazione pesata delle parole a partire dalle costanti generate da `build.py`
  - interroga `GET /api/daily` per sincronizzare la daily con timezone `Europe/Rome`
  - include fallback locale se il backend non risponde
  - oggi include anche il controllo di aggiornamento daily al rientro sulla scheda tramite `visibilitychange` e `focus`, con debounce, per evitare che resti visibile la daily del giorno precedente
  - nel popup finale puo' mostrare anche una definizione breve della parola soluzione tramite bottone `ⓘ`, se la parola e' presente in `DEFINIZIONI`

#### Backend e logging

- `serve_local.py`
  - e' il backend operativo unico del progetto
  - serve i file statici da `dist/`
  - espone `GET /api/daily` e `POST /api/attempt`
  - inizializza automaticamente `data/playtest.db`
  - salva gli eventi di gioco nella tabella `playtest_events`
  - gestisce CORS per frontend su origine separata
  - ricostruisce l'IP reale del client quando gira dietro reverse proxy locale

- `run_backend_service.sh`
  - wrapper di produzione per avviare `serve_local.py`
  - legge configurazione da file env
  - puo' opzionalmente lanciare `build.py` prima dell'avvio
  - e' pensato per essere chiamato da `systemd`

#### Test locale e avvio manuale

- `serve_hybrid_local.sh`
  - simula in locale l'architettura finale con frontend e backend su origini separate
  - avvia backend con CORS esplicito
  - avvia anche un server statico per `dist/`
  - e' il modo piu' vicino alla produzione per testare il frontend prima del deploy

- `share_public.sh`
  - script rapido per esporre il backend su host/porta pubblici senza systemd
  - utile per sessioni di test manuali o debug
  - salva stdout e stderr in `data/serve_public.*.log`

#### Report e analisi dati

- `report_playtest.py`
  - e' il report standard del progetto
  - esporta tutto il DB in `data/playtest_events.csv`
  - genera un report sintetico in `docs/playtest_report.md`
  - oggi copre metriche base: eventi, partite concluse, win/loss, guess usati, guess rifiutati, IP osservati, ultimi eventi

- `docs/db_activity_last_2_weeks_2026-04-17.md`
  - snapshot analitico ad hoc sulle ultime due settimane
  - aggrega utenti, sessioni, flusso medio e vocaboli provati

- `docs/db_activity_manager_summary_2026-04-17.md`
  - lettura manageriale corta dello stesso dataset
  - serve come vista decisionale: top player, retention, confronto daily vs infinita, parole dominanti

#### Deploy e infrastruttura

- `.github/workflows/github-pages.yml`
  - automatizza il deploy del frontend statico su GitHub Pages
  - verifica la sintassi Python
  - invoca `build_github_pages.py`
  - pubblica `github_pages/` come artefatto Pages

- `duckdns/update_duckdns.sh`
  - mantiene aggiornato l'hostname DuckDNS del backend VPS

- `deploy/systemd/*`, `deploy/caddy/*`, `deploy/*.env.example`
  - contengono i template operativi per servizio backend, reverse proxy HTTPS e configurazione ambiente

#### Dati e output runtime

- `dist/`
  - contiene gli artefatti locali giocabili prodotti dalla build
  - non e' sorgente: e' output rigenerabile

- `github_pages/`
  - contiene il pacchetto statico pronto per la pubblicazione su Pages

- `data/`
  - contiene anche `vocabolario.json`, cioe' le decisioni editoriali versionate sul vocabolario
  - contiene `definizioni.json`, con le definizioni brevi associate alle parole soluzione
  - contiene il database SQLite reale, export CSV e log runtime
  - e' la parte viva del progetto durante il playtest

- `docs/`
  - raccoglie sia documentazione tecnica sia report generati
  - oggi e' anche il posto dove si sta accumulando la memoria operativa del progetto

Osservazione pratica: il progetto oggi funziona bene proprio perche' i ruoli sono semplici. `build.py` genera, `template_parole.html` gioca, `serve_local.py` serve e registra, gli script shell avviano, i report leggono il DB.

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

### 2026-04-09 — Selettore difficoltà, pesi a 3 livelli, regola doppie, messaggi vittoria

#### Modifica 1 — Regola doppie: livello minimo "alta"

In `classifica_difficolta` aggiunta una regola finale: ogni parola con lettere doppie che era classificata `bassissima`, `bassa` o `media` viene promossa ad `alta`. La regola si applica dopo tutti gli override manuali, quindi `altissima` rimane invariata.

Effetto: la distribuzione livelli si è spostata notevolmente verso `alta` (da ~197 a 375 parole), riducendo `bassissima` (da ~405 a 359), `bassa` (da ~320 a 267) e `media` (da ~322 a 243). Il totale rimane 1319.

Motivazione: le doppie sono punitive in Wordle (si può sprecare un tentativo a indovinare la posizione della lettera ripetuta), quindi è corretto che non appaiano come parole "facili" in modalità difficile.

#### Modifica 2 — Tre set di pesi per la modalità infinita

`PESI_INFINITA` rimosso, sostituito da tre varianti selezionabili:

| Set | Bassissima | Bassa | Media | Alta | Altissima |
|-----|-----------|-------|-------|------|-----------|
| Facile | 45% | 30% | 15% | 8% | 2% |
| Media | 25% | 25% | 25% | 18% | 7% |
| Difficile | 5% | 10% | 20% | 35% | 30% |
| Daily | 10% | 20% | 35% | 25% | 10% |

I pesi daily sono stati aggiornati per favorire parole medie e alte (la daily dovrebbe essere una sfida condivisa più bilanciata verso il centro-alto della difficoltà).

Il blocco JS generato nella build ora include `PESI_CUM_INFINITA_FACILE`, `PESI_CUM_INFINITA_MEDIA`, `PESI_CUM_INFINITA_DIFFICILE` al posto del vecchio `PESI_CUM_INFINITA`.

#### Modifica 3 — Selettore difficoltà nell'header

Aggiunto un gruppo di tre pulsanti `Facile | Media | Difficile` nell'header, visibile **solo** in modalità infinita (nascosto in 24H).

Implementazione:
- HTML: `<div id="diff-selector">` con tre `.diff-btn` dentro l'`<header>`
- CSS: `header { flex-wrap: wrap; }` per permettere il secondo rigo su schermi piccoli; `#diff-selector { width: 100%; }` per occupare tutta la larghezza quando visibile; `.diff-btn.active` con sfondo accent per evidenziare la selezione
- JS: costante `DIFF_KEY = "infinita_difficolta"`, variabile `let difficoltaInfinita = "media"`, funzioni `getDifficoltaSalvata()` / `saveDifficolta()` / `aggiornaDiffSelector()`
- La selezione è persistente via `localStorage` con default `"media"`
- Cambiare difficoltà non riavvia la partita in corso (ha effetto dalla partita successiva)
- `aggiornaHeader()` gestisce show/hide del selettore e aggiornamento del pulsante attivo
- `scegliSoluzioneCasuale()` usa `pesiMap[difficoltaInfinita]` per selezionare il set di pesi corretto

Testato: su viewport 375px (iPhone SE) il selettore appare come secondo rigo sotto logo+pulsanti, senza overflow.

#### Modifica 4 — Messaggi vittoria neutri

Sostituiti i messaggi di vittoria nella funzione `renderFinePartita` con testi neutri senza genere e senza emoji:

| Tentativo | Prima | Dopo |
|-----------|-------|------|
| 1 | Perfetto! 🎉 | Incredibile! |
| 2 | Ottima! 🌟 | Eccellente! |
| 3 | Brava! 👏 | Ottimo! |
| 4 | Bene! 😊 | Bene! |
| 5 | Ci siamo quasi 😅 | Per un pelo! |
| 6 | Per un pelo! 😤 | Ce l'hai fatta! |

Il messaggio di sconfitta "Fine partita 😔" non è stato modificato.

### 2026-04-18 — Aggiornamento daily al rientro sulla scheda e fotografia analytics

#### Modifica frontend — refresh daily al ritorno su tab visibile

Problema emerso su Chrome mobile: lasciando aperta la pagina durante il cambio daily, al rientro restava visibile la parola vecchia finche' l'utente non ricaricava manualmente.

Fix applicato in `src/template_parole.html`:
- listener su `document.visibilitychange`
- listener di fallback su `window.focus`
- funzione dedicata `controllaAggiornamentoDaily()`
- debounce minimo per evitare doppie chiamate consecutive

Comportamento attuale:
- il controllo parte solo in modalita' `giornaliera`
- viene forzato un refresh dei metadati da `GET /api/daily`
- se `challenge_id` o `day_key` cambiano, il frontend resetta la partita in-place e ricarica la nuova daily
- se il backend non risponde, resta attivo il fallback locale gia' esistente
- la modalita' `infinita` non viene toccata

Effetto pratico: la daily ora si aggiorna automaticamente anche quando il giocatore torna alla pagina dopo mezzanotte Europe/Rome.

#### Modifica processo — analisi DB di periodo

Oltre al report standard `report_playtest.py`, sono stati prodotti due report aggiuntivi basati su query mirate sul DB:
- `docs/db_activity_last_2_weeks_2026-04-17.md`
- `docs/db_activity_manager_summary_2026-04-17.md`

Questi documenti introducono una vista piu' utile per il prodotto:
- utenti attivi e ricorrenti
- sessioni daily vs non-daily
- flusso medio giornaliero
- top player
- parole piu' provate
- soluzioni viste per modalita'

Il report standard resta utile come export rapido, ma l'analisi decisionale oggi passa anche da questi snapshot periodici.

### 2026-04-18 — Override vocabolario esternalizzati in JSON

Fino a oggi le decisioni editoriali sul vocabolario erano mischiate alla logica di build dentro `build.py`, sotto forma di set Python hardcoded.

Refactor applicato:
- creato `data/vocabolario.json` come file dati versionato
- spostati fuori dal codice:
  - `sempre_comuni`
  - `da_rimuovere`
  - `aggiunte`
  - `override_livello`
- `build.py` ora carica il file a runtime con una funzione dedicata
- gli override manuali non coprono piu' solo `alta` e `altissima`, ma anche `media` e `bassa`

Ordine di priorita' attuale nella classificazione:
1. `sempre_comuni` → `bassissima`
2. override `altissima`
3. override `alta`
4. override `media`
5. override `bassa`
6. `aggiunte` → `media` se non gia' assegnate
7. regola doppie → livello minimo `alta`

Effetto organizzativo:
- `build.py` torna a contenere soprattutto logica
- `data/vocabolario.json` diventa il punto unico in cui modificare le scelte editoriali
- ogni build logga anche quanti override sono stati caricati dal file JSON

Verifica eseguita sulla build corrente:
- `birba`, `calca`, `pigli` assenti dalle `soluzioni`
- `troia`, `negro`, `negra`, `negri`, `froci` presenti nelle `soluzioni`
- `docs/build_log.md` aggiornato con il riepilogo degli override caricati

### 2026-04-18 — Definizioni nel popup di fine partita

E' stato aggiunto un nuovo layer editoriale leggero per dare piu' contesto alla soluzione senza toccare la logica di gioco.

Modifica build:
- introdotto `data/definizioni.json` come archivio versionato delle definizioni brevi
- `build.py` ora carica il file e lo serializza nel blocco JS del template come costante `DEFINIZIONI`
- la build continua a funzionare anche se il file manca, usando un oggetto vuoto

Modifica frontend:
- nel modal finale `#m-end` la parola soluzione ora sta dentro una riga con bottone `ⓘ`
- click su `ⓘ` apre o richiude una `def-box` sotto la parola
- il bottone compare solo se la soluzione corrente ha una definizione disponibile
- a ogni nuova apertura del popup la definizione riparte chiusa

Effetto pratico: il gioco resta interamente statico lato frontend, ma il popup finale puo' offrire una spiegazione rapida della parola senza chiamate backend aggiuntive.

---

## Stato operativo attuale (2026-04-18)

| Componente | Stato |
|------------|-------|
| Frontend di gioco | template unico in `src/template_parole.html`, con modalita' daily/infinita, stato locale, sync daily da backend e refresh automatico al ritorno sulla scheda |
| Build | pipeline centrata su `build.py`, con export Pages tramite `build_github_pages.py` e iniezione di vocabolario + definizioni nel template |
| Backend | `serve_local.py` resta il backend unico del progetto: static serving + API + SQLite |
| Deploy statico | workflow GitHub Pages presente e operativo nel repo |
| Runtime backend | wrapper `run_backend_service.sh` e asset deploy (`systemd`, `Caddy`, `DuckDNS`) presenti e documentati |
| Analytics | report standard + due report ad hoc sulle ultime due settimane presenti in `docs/` |
| Database SQLite | `1196` eventi totali registrati, ultimo evento `2026-04-18 10:50:11` |

### Metriche e osservazioni correnti

- Il DB contiene oggi `1196` eventi grezzi; di questi `1118` sono traffico pubblico e `78` sono test locali/tecnici.
- Nei report sulle ultime 2 settimane (finestra `2026-04-04 -> 2026-04-17`) risultano `32` giocatori unici pubblici, `124` sessioni, `66` daily e `58` non-daily.
- Il flusso medio del periodo e' `8.86` sessioni/giorno, `4.57` utenti/giorno e `52.29` eventi/giorno.
- La daily oggi appare leggermente piu' efficiente della infinita: meno tentativi medi e win rate piu' alto.
- Il traffico resta concentrato: i primi 6 client generano oltre meta' delle sessioni del periodo analizzato.

### Vocabolario finale

- La build corrente del `2026-04-18` riporta `1319` soluzioni e `7804` tentativi.
- Gli override editoriali sono ora esternalizzati in `data/vocabolario.json`.
- Le definizioni brevi delle soluzioni sono ora versionate in `data/definizioni.json` e iniettate nel frontend come `DEFINIZIONI`.
- Il `build_log.md` attuale registra anche il riepilogo override: `42` comuni, `16` da_rimuovere, `5` aggiunte, `91` override di livello.
- `dist/` e `docs/build_log.md` risultano ora riallineati sui conteggi del vocabolario.

### Punto di maturita' del progetto

Ad oggi il progetto non e' piu' solo un prototipo front-end:
- ha una pipeline di build chiara
- ha un backend leggero ma stabile
- ha deploy statico separato dal backend
- ha logging persistente reale
- ha gia' iniziato a produrre analisi di prodotto, non solo log tecnici

Il principale passo successivo non e' tanto "farlo funzionare", quanto consolidare e automatizzare meglio cio' che gia' funziona: riallineare build/documentazione, dare forma stabile ai report analytics e decidere come usare i dati per tarare vocabolario e modalita'.

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
