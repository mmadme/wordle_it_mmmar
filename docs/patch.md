# Patch Plan - GitHub Version

## Scopo

Questo file descrive il piano di aggiornamento della copia di lavoro `woordle_new_github`.

Obiettivo principale:

- preparare una nuova versione del progetto adatta a una futura architettura ibrida
- frontend statico pubblicabile su GitHub Pages
- backend Python + SQLite mantenuto sulla VPS Ubuntu
- nessuna modifica alla versione attiva `woordle_new` finche' la nuova variante non e' pronta

Questo documento va aggiornato durante il lavoro: ogni step completato, decisione tecnica, blocco, deviazione dal piano o test rilevante deve essere annotato qui.

---

## Vincoli

- non toccare `woordle_new`, che e' la versione attiva
- lavorare solo dentro `woordle_new_github`
- preservare il funzionamento locale attuale del gioco
- preservare il logging playtest su SQLite
- evitare rotture della daily, della modalita' infinita e del vocabolario
- mantenere il progetto eseguibile su Ubuntu VPS

---

## Stato iniziale

Cartella di lavoro:

- `/home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github`

Origine:

- duplicato di `woordle_new` creato il `2026-04-05`

Caratteristiche ereditate:

- build tramite `build.py`
- frontend HTML singolo generato da `src/template_parole.html`
- server Python locale in `serve_local.py`
- database SQLite in `data/playtest.db`
- report in `report_playtest.py`
- avvio pubblico VPS tramite `share_public.sh`

Punto di partenza tecnico:

- il progetto attuale funziona in locale e su VPS
- il logging SQLite e' attivo quando il frontend raggiunge il backend
- la copia risultato usa ora anche un fallback compatibile con HTTP
- il progetto non e' ancora strutturato per frontend statico separato da backend API

---

## Obiettivo finale della patch

Arrivare a una versione che consenta:

- deploy del frontend statico su GitHub Pages
- backend API separato sulla VPS
- endpoint API configurabile dal frontend
- compatibilita' CORS esplicita
- possibilita' di usare un hostname fisso per il backend
- mantenimento del DB SQLite e del flusso di report esistente

Deliverable attesi:

- frontend statico buildabile e pubblicabile separatamente
- backend VPS riusabile come API remota
- documentazione aggiornata del flusso ibrido
- checklist di test per verificare il funzionamento end-to-end

---

## Strategia generale

Il lavoro va fatto in piu' fasi piccole, con test a ogni passaggio.

Principio guida:

- prima rendere il frontend configurabile
- poi rendere il backend piu' pulito come API
- poi testare la separazione frontend/backend in locale
- solo dopo preparare il deploy GitHub Pages

Questo riduce il rischio di introdurre troppe variabili insieme.

---

## Fase 0 - Baseline e fotografia iniziale

### Obiettivo

Congelare lo stato di partenza della copia `woordle_new_github`.

### Attivita'

- verificare che `build.py` completi la build senza errori
- verificare che `serve_local.py` parta correttamente su Ubuntu
- verificare che `report_playtest.py` legga correttamente il DB
- annotare gli endpoint attuali usati dal frontend
- annotare dove viene costruito l'URL delle API nel template

### Output atteso

- baseline tecnica documentata
- elenco file da toccare nella patch

### Criteri di completamento

- build eseguita
- server avviabile
- endpoint `/api/attempt` identificato
- punti di integrazione frontend/backend noti

### Note di avanzamento

- [x] completata
- note:
  - `python3 -m py_compile build.py serve_local.py report_playtest.py`: ok
  - `python3 build.py`: ok
  - endpoint playtest identificato in `src/template_parole.html` come `fetch("/api/attempt", ...)`
  - endpoint backend confermato in `serve_local.py` come `POST /api/attempt`
  - backend gia' compatibile a livello base con `OPTIONS /api/...` e `Access-Control-Allow-Origin: *`

---

## Fase 1 - Rendere configurabile la base URL delle API

### Obiettivo

Permettere al frontend di scegliere se chiamare:

- backend locale stesso host
- backend remoto su VPS

senza duplicare la logica del gioco.

### Attivita'

- introdurre nel frontend una configurazione `API_BASE_URL`
- mantenere compatibilita' con il comportamento attuale quando la config non e' impostata
- aggiornare i punti `fetch()` che oggi usano path relativi
- evitare hardcode sparsi dell'URL API
- scegliere una sola fonte di verita' per la configurazione

### Scelta consigliata

Usare una variabile globale semplice nel template, per esempio:

- `window.WOORDLE_API_BASE_URL`

con fallback a stringa vuota:

- `""` in locale
- `"https://api.example.com"` nella versione remota

### Output atteso

- frontend ancora funzionante in locale
- API remota selezionabile senza cambiare codice in piu' punti

### Criteri di completamento

- almeno una build locale testata
- nessuna regressione sui log playtest
- una sola costante/config governa l'endpoint

### Note di avanzamento

- [x] completata
- note:
  - introdotta costante globale `API_BASE_URL` nel frontend
  - introdotta funzione `apiUrl(path)` come unica costruzione dell'endpoint API
  - fallback locale preservato con `window.WOORDLE_API_BASE_URL` assente o vuota
  - `fetch("/api/attempt", ...)` sostituito con `fetch(apiUrl("/api/attempt"), ...)`
  - la configurazione prevista per la variante remota resta `window.WOORDLE_API_BASE_URL = "https://api.example.com"` oppure equivalente

---

## Fase 2 - Ripulire il backend come API remota

### Obiettivo

Far funzionare `serve_local.py` non solo come server statico locale, ma come backend API stabile per un frontend esterno.

### Attivita'

- verificare `OPTIONS /api/...`
- verificare header CORS su `POST /api/attempt`
- decidere se mantenere `Access-Control-Allow-Origin: *` o restringerlo
- aggiungere logging HTTP minimo utile per debug
- verificare il comportamento degli errori payload non validi
- verificare che il DB venga inizializzato sempre correttamente

### Miglioramenti consigliati

- logging semplice di `GET`, `POST` e status code
- configurazione opzionale dell'origine consentita
- messaggi di errore piu' chiari nei casi di payload malformato

### Output atteso

- backend testabile anche senza frontend locale
- diagnosi piu' facile in caso di problemi da GitHub Pages

### Criteri di completamento

- `POST /api/attempt` testato da host esterno o simulato
- preflight `OPTIONS` verificato
- log backend leggibili

### Note di avanzamento

- [x] completata
- note:
  - aggiunto supporto `--allow-origin` per configurare le origini API consentite
  - aggiunto supporto `--log-http` per vedere log HTTP minimi in debug
  - centralizzati gli header CORS per tutte le risposte API, incluse `OPTIONS`, `204`, `400` e `404`
  - `POST /api/attempt` ora restituisce errore JSON coerente in caso di payload non valido
  - testato preflight `OPTIONS /api/attempt` con origine `https://example.github.io`
  - testato `POST /api/attempt` con origine consentita e risposta `204`
  - testato errore `400` con payload non JSON e header CORS corretti
  - verificato inserimento reale nel DB SQLite con sessione `phase2-test`

---

## Fase 3 - Test di separazione frontend/backend in locale

### Obiettivo

Simulare l'architettura ibrida prima del deploy reale.

### Attivita'

- servire il frontend statico da un'origine separata
- tenere il backend sulla VPS o su una porta diversa
- configurare il frontend per usare la API remota
- verificare che il browser non blocchi le chiamate
- verificare che gli eventi finiscano in SQLite

### Esempio di simulazione

- frontend su una porta A
- backend su una porta B
- host diversi o almeno origini diverse

Lo scopo e' far emergere subito:

- problemi CORS
- problemi di mixed content
- path API sbagliati
- errori di fetch silenziosi

### Output atteso

- una prova locale realistica del modello ibrido

### Criteri di completamento

- il gioco si apre
- una partita produce record nel DB
- il report continua a funzionare

### Note di avanzamento

- [x] completata
- note:
  - introdotto override pratico di `API_BASE_URL` anche tramite query string `?api_base=...`
  - introdotta persistenza locale di `API_BASE_URL` tramite chiave `parole_api_base_url`
  - aggiunto script `serve_hybrid_local.sh` per simulare frontend statico e backend API su origini separate
  - frontend statico servito localmente su `http://127.0.0.1:4173`
  - backend API servito localmente su `http://127.0.0.1:8014`
  - verificato caricamento del frontend statico con risposta `200`
  - verificato preflight `OPTIONS /api/attempt` con origine `http://127.0.0.1:4173`
  - verificato `POST /api/attempt` con origine `http://127.0.0.1:4173` e risposta `204`
  - verificato inserimento reale nel DB SQLite con sessione `phase3-test`
  - `report_playtest.py` eseguito con successo dopo la simulazione

---

## Fase 4 - Preparare il frontend per GitHub Pages

### Obiettivo

Fare in modo che la build statica sia pubblicabile senza dipendere dalla struttura attuale della VPS.

### Attivita'

- verificare path asset e riferimenti interni
- decidere se pubblicare da root repo o da sottocartella
- verificare eventuali problemi con path assoluti/relativi
- preparare una modalita' di build o configurazione per GitHub Pages
- documentare il flusso di pubblicazione

### Decisioni da prendere

- repo dedicata o cartella pubblicata dentro repo esistente
- branch `gh-pages` oppure deploy da `main`
- URL finale previsto

### Step operativi su GitHub

Questa sezione elenca i passaggi da fare direttamente su GitHub quando iniziera' il deploy del frontend.

#### Opzione consigliata per questa patch

Per il progetto attuale la scelta consigliata e':

- repository dedicata al frontend statico, oppure repository separata di test
- deploy tramite branch semplice se vogliamo minimizzare complessita'
- valutare GitHub Actions solo se la build/deploy diventa piu' articolata

Motivo:

- il progetto produce gia' file statici pronti in `dist/`
- per una prima iterazione GitHub Pages da branch e' piu' semplice da diagnosticare
- GitHub documenta sia la pubblicazione da branch sia quella tramite GitHub Actions

#### Step minimi da fare su GitHub

1. Creare o scegliere il repository che conterra' il frontend statico.
2. Decidere se pubblicare:
   - dalla root del branch
   - oppure dalla cartella `/docs` del branch
3. Caricare nel repository i file statici da pubblicare.
4. Aprire il repository su GitHub.
5. Andare in `Settings` -> `Pages`.
6. In `Build and deployment`, scegliere la sorgente di pubblicazione:
   - branch, se pubblichiamo direttamente file statici
   - GitHub Actions, se vogliamo un workflow di deploy
7. Se si usa il deploy da branch:
   - scegliere branch
   - scegliere cartella `/` oppure `/docs`
8. Salvare la configurazione.
9. Attendere che GitHub Pages pubblichi il sito.
10. Annotare l'URL risultante nel piano patch.

#### Decisione pratica da fissare prima del deploy

Conviene decidere una delle due strade e mantenerla stabile:

- `main` + cartella `/docs`
- branch dedicato `gh-pages` + root `/`

Per questa patch, la strada da valutare per prima e':

- repository frontend dedicata
- file statici pubblicati dalla root del branch

Questo evita di mescolare codice sorgente, file statici generati e materiali di backend nello stesso repository di produzione.

#### Step aggiuntivi se usiamo GitHub Actions

Se scegliamo GitHub Actions come sorgente di pubblicazione:

1. Configurare `Settings` -> `Pages` con `Source: GitHub Actions`.
2. Aggiungere un workflow che:
   - prepara i file statici
   - pubblica l'artefatto Pages
3. Verificare che il workflow venga eseguito sul branch corretto.
4. Annotare nel piano patch:
   - nome del workflow
   - branch trigger
   - cartella sorgente della build

#### Step aggiuntivi se in futuro usiamo un custom domain

Questo non e' necessario per la Fase 4, ma va tenuto in mente.

1. Aprire `Settings` -> `Pages`.
2. Inserire il custom domain.
3. Aggiornare i record DNS dal provider del dominio.
4. Verificare HTTPS e stato del certificato.

#### Note operative importanti

- GitHub Pages e' adatto al solo frontend statico, non al backend Python
- se pubblichiamo da `/docs`, quella cartella non deve sparire dal branch selezionato
- se in futuro il repository conterra' symlink o un deploy piu' complesso, GitHub raccomanda GitHub Actions
- l'URL finale va riportato in `docs/patch.md` appena disponibile

### Output atteso

- pacchetto statico pronto per Pages
- istruzioni di deploy ripetibili

### Criteri di completamento

- la build si apre correttamente in un contesto statico
- nessuna chiamata rompe la pagina se l'API non e' raggiungibile

### Note di avanzamento

- [x] completata
- note:
  - verificato che `git` e' gia' disponibile sul sistema (`git version 2.43.0`)
  - aggiunto `api-config.js` come file statico caricato dal frontend
  - `build.py` ora genera anche `dist/api-config.js`
  - aggiunto `build_github_pages.py` per esportare un pacchetto statico ripetibile
  - introdotta cartella di output `github_pages/`
  - il pacchetto export include `index.html`, `parole-infinito.html`, `404.html`, `api-config.js` e `.nojekyll`
  - verificata esportazione con `python3 build_github_pages.py --api-base https://api.example.com`
  - verificato serving statico di `github_pages/` su `http://127.0.0.1:4174`
  - verificati `index.html`, `parole-infinito.html` e `api-config.js` con risposta `200`

---

## Fase 5 - Definire l'hostname del backend

### Obiettivo

Dare al backend un endpoint stabile da usare dal frontend statico.

### Opzioni da valutare

- IP pubblico + porta
- subdominio gratuito tipo DuckDNS
- dominio/subdominio con reverse proxy

### Raccomandazione iniziale

Per test rapidi:

- subdominio gratuito

Per soluzione piu' pulita:

- hostname stabile + reverse proxy + HTTPS

### Nota importante

Se il frontend finira' su GitHub Pages, il backend in solo HTTP puo' causare blocchi browser per mixed content.

Questa fase quindi va letta anche in funzione di:

- disponibilita' HTTPS
- facilita' di deploy
- costo zero o quasi

### Output atteso

- URL stabile scelto per il backend
- percorso di migrazione verso HTTPS chiaro

### Criteri di completamento

- backend raggiungibile da browser esterno con hostname fisso

### Note di avanzamento

- [x] completata
- note:
  - scelta iniziale fissata su DuckDNS come hostname stabile gratuito del backend
  - aggiunto script `duckdns/update_duckdns.sh` per aggiornare il record DNS dal server
  - aggiunto file `duckdns/duckdns.env.example` per configurare dominio e token
  - aggiunta guida operativa `docs/backend_hostname_duckdns.md`
  - configurazione reale DuckDNS presente con dominio `sborraparle`
  - cron job confermato con esecuzione ogni 5 minuti
  - log DuckDNS verificato con ultimo stato `OK`
  - `sborraparle.duckdns.org` risolve verso `92.4.220.150`
  - backend verificato raggiungibile via `http://sborraparle.duckdns.org:8015/parole-infinito.html`
  - HTTPS del backend resta fuori da questa fase e verra' trattato successivamente

---

## Fase 6 - Stabilizzare il deploy backend sulla VPS

### Obiettivo

Evitare avvio manuale fragile e migliorare affidabilita' del backend.

### Attivita'

- decidere se mantenere `share_public.sh` come utility di avvio
- valutare un servizio `systemd`
- separare chiaramente avvio backend da eventuale build frontend
- definire percorso log backend
- verificare persistenza delle regole firewall necessarie

### Output atteso

- backend riavviabile in modo prevedibile
- meno dipendenza da sessione shell aperta

### Criteri di completamento

- backend riavvia senza interventi manuali lunghi
- log diagnostici consultabili

### Note di avanzamento

- [x] completata
- note:
  - aggiunti `run_backend_service.sh`, `deploy/backend.env.example` e `deploy/systemd/woordle-backend.service`
  - aggiunti anche `deploy/backend-test.env.example` e `deploy/systemd/woordle-backend-test.service` per prove su porta separata
  - aggiunta guida `docs/backend_service_systemd.md`
  - soluzione scelta: `systemd` con file ambiente separato e restart automatico
  - `woordle-backend-test.service` risulta `active` ed `enabled`
  - la porta `8015` e' stata confermata come porta definitiva del backend per questa variante
  - `curl -I http://127.0.0.1:8015/parole-infinito.html` -> `200`
  - `curl -I http://sborraparle.duckdns.org:8015/parole-infinito.html` -> `200`

---

## Fase 7 - Test end-to-end reale

### Obiettivo

Verificare che la versione ibrida funzioni davvero in scenario reale.

### Attivita'

- aprire il frontend dalla sua URL statica
- giocare almeno una partita completa
- generare almeno un tentativo rifiutato
- verificare i `POST /api/attempt`
- controllare il DB SQLite
- rigenerare `playtest_events.csv`
- rigenerare `playtest_report.md`

### Casi da coprire

- modalita' infinita
- modalita' giornaliera
- vittoria
- sconfitta
- condivisione risultato
- assenza regressioni UI

### Output atteso

- prova concreta che il nuovo assetto e' operativo

### Criteri di completamento

- frontend raggiungibile
- eventi scritti nel DB
- report coerente

### Note di avanzamento

- [ ] completata
- note:

---

## Fase 8 - Chiusura patch e decisione di rollout

### Obiettivo

Decidere se la nuova variante e' pronta per sostituire o affiancare la versione attiva.

### Attivita'

- riassumere differenze tra `woordle_new` e `woordle_new_github`
- elencare rischi residui
- aggiornare `CHANGELOG.md`
- aggiornare `stato_progetto.md`
- decidere strategia di promozione

### Possibili esiti

- tenere `woordle_new_github` come ramo sperimentale
- promuoverla a nuova versione primaria
- usare solo alcune patch nella versione attiva

### Criteri di completamento

- decisione esplicita presa
- documentazione aggiornata

### Note di avanzamento

- [ ] completata
- note:

---

## File candidati alla modifica

Frontend:

- `src/template_parole.html`
- `dist/parole-infinito.html`
- eventualmente `build.py` se serve iniettare configurazione o varianti di build

Backend:

- `serve_local.py`
- `share_public.sh`
- `serve_hybrid_local.sh`

Documentazione:

- `docs/patch.md`
- `docs/CHANGELOG.md`
- `docs/stato_progetto.md`
- `docs/backend_hostname_duckdns.md`
- `docs/backend_service_systemd.md`
- `docs/backend_https_caddy.md`

Operativita' / deploy:

- eventuali nuovi script di build o deploy
- eventuali file di servizio o reverse proxy, se introdotti piu' avanti
- `duckdns/update_duckdns.sh`
- `duckdns/duckdns.env.example`
- `run_backend_service.sh`
- `deploy/backend.env.example`
- `deploy/backend-test.env.example`
- `deploy/systemd/woordle-backend.service`
- `deploy/systemd/woordle-backend-test.service`
- `deploy/caddy/Caddyfile.example`

---

## Rischi principali

### 1. Mixed content

Se il frontend e' in HTTPS e il backend in HTTP, il browser puo' bloccare le chiamate API.

Mitigazione:

- prevedere presto una strategia HTTPS per il backend

### 2. CORS incompleto

Le richieste possono fallire anche se il backend e' raggiungibile.

Mitigazione:

- testare esplicitamente `OPTIONS` e header `Access-Control-*`

### 3. Configurazione sparsa

Se l'URL API finisce hardcoded in piu' punti, la manutenzione diventa fragile.

Mitigazione:

- una sola costante/config globale

### 4. Rottura del flusso locale

Potremmo migliorare la variante GitHub ma rompere l'uso locale.

Mitigazione:

- fallback locale come comportamento predefinito

### 5. Regressioni gameplay

Una patch infrastrutturale non deve rompere gioco, daily o statistiche.

Mitigazione:

- testare sempre le funzionalita' core dopo ogni modifica

---

## Cose da non fare

- non modificare `woordle_new`
- non mischiare subito deploy GitHub Pages, HTTPS, DNS e refactor frontend in un unico step
- non saltare i test intermedi
- non dare per scontato che il browser segnali bene tutti gli errori cross-origin
- non introdurre piu' fonti di configurazione API senza motivo

---

## Checklist sintetica

- [x] baseline tecnica confermata
- [x] `API_BASE_URL` introdotta
- [x] backend compatibile con richieste cross-origin
- [x] test locale frontend/backend separati eseguito
- [x] build pronta per GitHub Pages
- [x] hostname backend deciso
- [x] strategia HTTPS chiarita
- [x] deploy VPS backend stabilizzato
- [ ] test end-to-end reale completato
- [ ] documentazione finale aggiornata

---

## Diario operativo

Usare questa sezione come log breve e cumulativo.

### 2026-04-05

- creata copia separata `woordle_new_github`
- deciso di non toccare la versione attiva `woordle_new`
- aperto il cantiere per futura variante GitHub Pages + backend VPS
- completata la baseline tecnica iniziale della copia di lavoro
- completata la prima introduzione di `API_BASE_URL` nel frontend con fallback locale
- verificati anche `report_playtest.py` e uno smoke test di avvio server sulla copia GitHub
- completata la prima pulizia del backend come API remota con CORS configurabile e log HTTP minimi
- completata la simulazione locale frontend/backend separati con script dedicato
- completata la preparazione del pacchetto statico ripetibile per GitHub Pages
- completata la definizione dell'hostname stabile del backend con DuckDNS
- chiarita la strategia HTTPS del backend con Caddy davanti al servizio Python
- completata la stabilizzazione del backend VPS su `8015` con servizio `systemd` attivo
- configurato Caddy come reverse proxy su `80/443` con redirect HTTP locale funzionante
- verificato che l'emissione del certificato TLS e' bloccata da timeout esterno su `92.4.220.150:80/443`, quindi resta da completare l'apertura pubblica lato Oracle Cloud

---

## Prossimo step consigliato

Prossimo intervento da fare:

- completare l'apertura pubblica di `80/443` lato Oracle Cloud e ritestare il certificato HTTPS di Caddy

Motivo:

- frontend GitHub Pages, hostname stabile, servizio `systemd` e reverse proxy locale sono gia' pronti
- il blocco principale rimasto per l'architettura finale e' il timeout esterno sul challenge TLS di Let's Encrypt
- appena `https://sborraparle.duckdns.org` rispondera' correttamente potremo rigenerare `github_pages/api-config.js` con l'URL finale

## Riferimenti ufficiali

- GitHub Pages publishing source: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- GitHub Pages custom domains: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages
