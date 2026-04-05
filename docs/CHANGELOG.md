# Changelog

## 2026-04-05 - Scaffolding repository GitHub

### Aggiunto

- `README.md` con panoramica del progetto, architettura ibrida, comandi principali e flusso GitHub Pages.
- `.gitignore` per escludere build artefacts, database locali, log e segreti runtime.
- `.github/workflows/github-pages.yml` per buildare e pubblicare automaticamente il frontend statico su GitHub Pages.
- `docs/github_repo_setup.md` con i passaggi minimi per inizializzare la repo, collegare il remoto e attivare Pages.

### Verificato

- `python3 -m py_compile build.py build_github_pages.py serve_local.py report_playtest.py`
- `python3 build_github_pages.py --api-base https://<backend-domain>`

## 2026-04-05 - Fase HTTPS backend con Caddy

### Modificato

- `deploy/caddy/Caddyfile.example` semplificato con dominio placeholder e reverse proxy verso `127.0.0.1:8015`.
- `docs/backend_https_caddy.md` aggiornato con la procedura reale adottata sulla VPS e con la diagnostica del blocco residuo.
- `docs/patch.md` aggiornato con lo stato corrente del reverse proxy HTTPS.

### Verificato

- `caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`
- `caddy.service` attivo dopo `restart`
- listener locali attivi su `*:80` e `*:443`
- `curl -I --resolve <backend-domain>:80:127.0.0.1 http://<backend-domain>` con `308 Permanent Redirect`

### Blocco aperto

- emissione certificato TLS ancora dipendente dalla raggiungibilita' pubblica di `80/443`, quindi lato Oracle Cloud va sempre verificata l'apertura esterna

## 2026-04-05 - Piano patch GitHub

### Aggiunto

- Nuovo file `docs/patch.md` con roadmap dettagliata per evolvere `woordle_new_github` verso una struttura frontend statico + backend VPS.
- Sezioni operative con fasi, criteri di completamento, rischi, checklist e diario di avanzamento.

## 2026-04-05 - Fase 0 e Fase 1 patch GitHub

### Modificato

- `src/template_parole.html` aggiornato con `API_BASE_URL` e helper `apiUrl(path)` per separare frontend statico e backend remoto senza rompere il fallback locale.

### Verificato

- Baseline tecnica iniziale confermata su `woordle_new_github`.
- `python3 -m py_compile build.py serve_local.py report_playtest.py`
- `python3 build.py`
- `python3 report_playtest.py`
- smoke test di avvio `serve_local.py` sulla copia GitHub
- Punto unico di invio playtest identificato e reso configurabile.

## 2026-04-05 - Fase 2 patch GitHub

### Modificato

- `serve_local.py` aggiornato con `--allow-origin` per configurare le origini consentite delle API.
- `serve_local.py` aggiornato con `--log-http` per abilitare log HTTP minimi durante il debug.
- Header CORS centralizzati per le risposte API, incluse `OPTIONS`, `204`, `400` e `404`.
- Errori API resi piu' coerenti con risposta JSON per payload invalidi o endpoint non trovati.

### Verificato

- `python3 -m py_compile build.py serve_local.py report_playtest.py`
- `OPTIONS /api/attempt` con origine esplicita e risposta `204`
- `POST /api/attempt` con origine consentita e risposta `204`
- `POST /api/attempt` con payload non valido e risposta `400` JSON
- scrittura reale di un record SQLite con sessione `phase2-test`

## 2026-04-05 - Fase 3 patch GitHub

### Modificato

- `src/template_parole.html` aggiornato per leggere `API_BASE_URL` anche da query string (`api_base` / `apiBase`) e da `localStorage`.
- Aggiunto `serve_hybrid_local.sh` per simulare localmente frontend statico e backend API su origini diverse.

### Verificato

- frontend statico servito su origine separata con risposta `200`
- `OPTIONS /api/attempt` con origine `http://127.0.0.1:4173` e risposta `204`
- `POST /api/attempt` con origine `http://127.0.0.1:4173` e risposta `204`
- scrittura reale di un record SQLite con sessione `phase3-test`
- `python3 report_playtest.py` eseguito con successo dopo la simulazione

## 2026-04-05 - Piano GitHub Pages

### Modificato

- `docs/patch.md` esteso con gli step operativi da svolgere direttamente su GitHub per il deploy del frontend con GitHub Pages.
- Aggiunti riferimenti ufficiali GitHub Pages per publishing source e custom domain.

## 2026-04-05 - Fase 4 patch GitHub

### Modificato

- `src/template_parole.html` aggiornato per caricare `api-config.js` come configurazione statica del frontend.
- `build.py` aggiornato per generare anche `dist/api-config.js`.
- Aggiunto `build_github_pages.py` per esportare un pacchetto statico ripetibile in `github_pages/`.

### Verificato

- `git` gia' disponibile sul sistema (`git version 2.43.0`)
- `python3 -m py_compile build.py build_github_pages.py serve_local.py report_playtest.py`
- `python3 build.py`
- `python3 build_github_pages.py --api-base https://api.example.com`
- serving statico di `github_pages/` con `index.html`, `parole-infinito.html` e `api-config.js` raggiungibili con risposta `200`

## 2026-04-05 - Fase 5 avvio DuckDNS

### Modificato

- Aggiunto `duckdns/update_duckdns.sh` per aggiornare l'hostname DuckDNS dal backend VPS.
- Aggiunto `duckdns/duckdns.env.example` come base di configurazione locale.
- Aggiunta guida `docs/backend_hostname_duckdns.md` con i passaggi per creare e mantenere un hostname stabile gratuito.

### Verificato

- cron job DuckDNS presente ed attivo
- configurazione reale DuckDNS presente per un dominio dedicato non riportato nel repo pubblico
- risoluzione DNS verificata verso il public IP della VPS
- backend raggiungibile via hostname dedicato su porta `8015`

## 2026-04-05 - Fase 6 preparazione systemd

### Modificato

- Aggiunto `run_backend_service.sh` come wrapper stabile di avvio backend.
- Aggiunto `deploy/backend.env.example` per configurazione separata del servizio.
- Aggiunto `deploy/backend-test.env.example` per prove su porta separata.
- Aggiunto `deploy/systemd/woordle-backend.service` come unit file `systemd`.
- Aggiunto `deploy/systemd/woordle-backend-test.service` come unit file `systemd` per test.
- Aggiunta guida `docs/backend_service_systemd.md` con i passaggi di installazione e diagnostica.

### Note

- La fase e' preparata a livello di progetto, ma l'attivazione finale del servizio sulla VPS richiede ancora i comandi `sudo systemctl ...`.
- Per le prove iniziali e' consigliata la porta `8015` per non interferire con il backend attivo sulla `8000`.

## 2026-04-05 - Fase 6 attiva su 8015

### Modificato

- `serve_local.py`, `share_public.sh`, `run_backend_service.sh` e `deploy/backend.env.example` allineati a `8015` come porta definitiva della variante GitHub.
- Documentazione corrente aggiornata per usare `8015` come endpoint backend di riferimento.

### Verificato

- `woordle-backend-test.service` risulta `active`
- `woordle-backend-test.service` risulta `enabled`
- `curl -I http://127.0.0.1:8015/parole-infinito.html` -> `200`
- `curl -I http://<backend-domain>:8015/parole-infinito.html` -> `200`

## 2026-04-05 - Strategia HTTPS backend

### Modificato

- Aggiunto `deploy/caddy/Caddyfile.example` come base per reverse proxy HTTPS con Caddy.
- Aggiunta guida `docs/backend_https_caddy.md` per esporre il backend su un dominio HTTPS dedicato.

### Verificato

- Strategia tecnica definita: backend Python su `127.0.0.1:8015`, Caddy su `80/443`, certificati automatici e `reverse_proxy`.

## 2026-04-05 - Verifica Ubuntu

### Modificato

- Documentazione allineata a `build.py` come script di build effettivo.
- Aggiunte note esplicite sulla compatibilita' con Ubuntu e sull'uso di `python3`.
- Chiarito che `tools/cloudflared.exe` e' un asset Windows opzionale e non serve per l'esecuzione locale su Ubuntu.

### Verificato

- `python3 -m py_compile build.py serve_local.py report_playtest.py`
- `python3 build.py`
- `python3 serve_local.py --host 127.0.0.1 --port 8011`
- `GET /parole-infinito.html` con risposta HTTP `200`
- `POST /api/attempt` con risposta HTTP `204`
- `python3 report_playtest.py`

## 2026-03-26

### Aggiunto

- File `stato_progetto.md` con prompt iniziale, riepilogo progetto, problemi trovati, test eseguiti e stato corrente.
- Monitoraggio storico delle build in `build_history.md`, da aggiornare automaticamente a ogni esecuzione di `buildv2.py`.
- Questo file `CHANGELOG.md` per tracciare le modifiche funzionali e strutturali del progetto.

### Modificato

- `buildv2.py` aggiornato per distinguere tra forestierismi comuni, prestiti stabili e forestierismi da escludere.
- Aggiunta la scrematura dei tentativi con rimozione di parole troppo poco integrate come `jeans`, `share`, `shake`, `smoke`, `white`.
- Rimossa `jeans` dalle soluzioni.
- Migliorato il CSS responsive della tastiera su mobile.

### Verificato

- GUI desktop e mobile
- tastiera fisica e virtuale
- validazione parole
- toast di errore
- modali
- statistiche
- reset partita
- overflow mobile risolto

## Convenzione d'uso

- `CHANGELOG.md`: cambiamenti di progetto, funzionalità e decisioni manuali.
- `build_log.md`: dettaglio completo dell'ultima build.
- `build_history.md`: storico sintetico cumulativo delle build.
- `stato_progetto.md`: fotografia complessiva dello stato del progetto.

## 2026-03-26 - Rebalance e Riordino

### Aggiunto

- Nuovo `build.py` in radice come generatore unico del progetto.
- Cartella `dist/` per gli output finali del gioco.
- Cartella `docs/` per log, changelog e stato progetto.
- Cartella `src/` con `template_parole.html` come base HTML.

### Modificato

- Scrematura `soluzioni` aggiornata per mantenere i verbi al presente piu' naturali e spostare i tempi verbali piu' complessi nei soli tentativi.
- Rimossi cluster troppo ambigui con doppie e famiglie punitive come `detto`, `tetto`, `cassa`.
- Bilanciamento finale soluzioni portato a `1329` parole.
- Bilanciamento finale tentativi portato a `7800` parole.

### Rimosso

- Cartelle obsolete `prova1` e `prova2`.
- File temporanei e asset di test non piu' necessari.

### Verificato

- Build nuova eseguita con successo.
- Vocabolario HTML aggiornato correttamente.
- UI finale verificata via screenshot browser headless.
- Nuovo set soluzioni controllato anche con analisi quantitativa.

## 2026-03-26 - Share e tuning ulteriore

### Modificato

- `biada` rimossa dalle soluzioni.
- `sport` rimossa dalle soluzioni.
- Aggiunto pulsante `Condividi` nella modale finale.
- Aggiunta copia del risultato negli appunti in formato stile Par🇮🇹le con numero partita locale.

### Verificato

- `biada` e `sport` non sono piu' presenti in `dist/parole_soluzioni.txt`.
- Il bottone `Condividi` e la logica di copia risultano presenti nella build finale.

## 2026-03-26 - Modalita' giornaliera

### Aggiunto

- Selettore modalita' `24H` / `∞` nell'header.
- Modalita' giornaliera con parola uguale per tutti in base alla data locale.
- Stato partita e statistiche separate per modalita' infinita e giornaliera.
- Persistenza della sfida del giorno in `localStorage`.

### Modificato

- Il bottone principale della modale finale, in giornaliera, porta alla modalita' infinita invece di rigenerare una nuova daily.
- La condivisione in modalita' giornaliera usa l'identificatore della sfida del giorno.
- Testo di aiuto aggiornato per spiegare le due modalita'.
- Corretto il contatore locale della modalita' infinita per non saltare a `2` se la prima partita arriva dopo un passaggio iniziale dalla daily.

### Verificato

- Build eseguita con successo tramite `python build.py`.
- Presenza nella build finale di `btn-mode`, `parole_mode`, `parole_daily_state`, `parole_daily_stats`.
- Sintassi del JavaScript finale verificata con `node`.

## 2026-03-26 - Hosting statico locale per playtest

### Aggiunto

- Script `serve_local.py` per servire `dist/` in HTTP locale.

### Modificato

- Documentazione di progetto aggiornata con il flusso di test via rete locale.

### Verificato

- Script controllato a livello sintattico e pronto all'avvio da riga di comando.

## 2026-03-26 - Tunnel temporaneo per playtest remoto

### Aggiunto

- Cartella `tools/` con `cloudflared.exe` per esporre temporaneamente il server locale.

### Verificato

- Quick tunnel avviato verso `http://127.0.0.1:8000`.
- Pagina pubblica raggiungibile con risposta HTTP `200`.

## 2026-03-27 - Monitoraggio playtest su SQLite

### Aggiunto

- Database `data/playtest.db`.
- Endpoint `POST /api/attempt` nel server locale.
- Logging client-side di `accepted_guess`, `rejected_guess` e `game_end`.

### Modificato

- `serve_local.py` trasformato da server statico puro a server di playtest con SQLite.
- Il server locale è stato riavviato sulla stessa porta `8000` senza cambiare il link del tunnel pubblico.

### Verificato

- Build aggiornata e rigenerata.
- Endpoint API testato con risposta `204`.
- Riga di prova scritta correttamente in `playtest.db`.
- Link pubblico ancora raggiungibile con risposta HTTP `200`.

## 2026-03-27 - Fix modale finale dopo refresh

### Modificato

- Ripristino stato aggiornato per riaprire la modale finale se la partita era già conclusa.
- Introdotta una funzione dedicata al render della modale finale, riusata sia a fine partita sia dopo reload.

### Verificato

- Build rigenerata senza cambiare il link del tunnel.
- Presenza nella build finale del richiamo che riapre la modale al ripristino di una partita finita.

## 2026-03-27 - Fix encoding popup finale

### Modificato

- Corretto il rendering della modale finale dopo refresh usando stringhe Unicode stabili.
- Sistemata la griglia emoji del popup, che risultava corrotta negli screenshot dei tester.

### Verificato

- Build rigenerata mantenendo lo stesso link pubblico.
- Pagina pubblica ancora raggiungibile con risposta HTTP `200`.
## 2026-03-28 - Rebalance parole, default daily e mobile keyboard

### Modificato

- Rimosse dalle `soluzioni` ma mantenute nei `tentativi`: `bidet`, `cruna`, `biada`, `bitta`, `sport`, `torba`.
- Introdotta una classificazione `facili / medie / difficili` per le `soluzioni`.
- Aggiunta estrazione pesata:
  - infinita: circa `65%` facili, `25%` medie, `10%` difficili
  - giornaliera: parola deterministica ma con lo stesso schema pesato
- La modalita' iniziale di default ora e' `24H`.
- Dopo la chiusura della modale finale della daily, il gioco passa automaticamente all'infinita.
- Alzata la tastiera su mobile con piu' padding inferiore e tasti leggermente piu' alti.

### Verificato

- `python build.py` eseguito con successo.
- Build finale aggiornata con `modalitaIniziale`, `SOLUZIONI_FACILI`, `SOLUZIONI_MEDIE`, `SOLUZIONI_DIFFICILI`.
- Verificato che le parole escluse non compaiono piu' tra le `soluzioni` ma restano nei `tentativi`.

## 2026-03-28 - Report playtest corretto

### Modificato

- `report_playtest.py` ora conta le `soluzioni viste` sulle partite concluse (`game_end`) invece che sui guess accettati.
- Aggiunte nel report:
  - partite vinte
  - partite perse
  - media tentativi nelle vittorie
  - elenco delle soluzioni perse

### Verificato

- Script pronto a rigenerare `data/playtest_events.csv` e `docs/playtest_report.md` con metriche piu' affidabili.
