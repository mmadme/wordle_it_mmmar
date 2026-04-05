# Stato Progetto - Parole Infinito

## Prompt iniziale

Richiesta iniziale ricevuta:

> "ho bisogno che fai un po' di test al gioco parole infinito.html e verifichi la gui, se funziona se i tasti sono ok, se le parole hanno senso come soluzioni e come tentativi in italiano, le soluzioni non devono essere troppo difficili ma i tentativi sono comunque permesse, le parole devono essere italiane, non ci devono essere nomi propri o etnici"

Chiarimento successivo:

> "no, con etnici non intendo quelle ma intendo più inglesismi troppo forzati ( esempio: parole come sport sono accettate, jeans no)"

## Obiettivo del progetto

Costruire e mantenere un Wordle italiano in file singolo HTML, con:

- interfaccia semplice e funzionante su desktop e mobile
- tastiera virtuale e fisica corrette
- soluzioni da 5 lettere comprensibili e non troppo ostiche
- tentativi validi in italiano, ma senza forestierismi troppo forzati
- generazione automatica di HTML e liste parole tramite `build.py`

## File principali del progetto

- `build.py`: generatore del gioco, delle liste parole e del log
- `parole-infinito.html`: gioco finale apribile nel browser
- `parole_soluzioni.txt`: elenco parole possibili come soluzione
- `parole_tentativi.txt`: elenco parole accettate come tentativo
- `build_log.md`: log dell'ultima build
- `build_history.md`: storico sintetico di tutte le build
- `CHANGELOG.md`: registro modifiche del progetto

## Verifiche eseguite finora

### Audit iniziale del progetto

Sono stati controllati:

- struttura della cartella
- logica JS dentro `parole-infinito.html`
- processo di generazione in `build.py`
- liste parole in `parole_soluzioni.txt` e `parole_tentativi.txt`

### Test funzionali GUI e gioco

Test browser automatizzati eseguiti su `parole-infinito.html`:

- caricamento pagina corretto
- griglia 6x5 presente
- tastiera virtuale completa con 28 tasti
- input da tastiera fisica funzionante
- input da tastiera virtuale funzionante
- `Backspace` funzionante
- toast per parola troppo corta
- toast per parola non presente nel dizionario
- aggiornamento colori in griglia
- aggiornamento colori tastiera
- blocco input quando una modale è aperta
- apertura modale finale a vittoria
- salvataggio statistiche in `localStorage`
- reset corretto con "Nuova partita"
- verifica layout mobile

## Problemi trovati

### 1. Forestierismi troppo forzati nel vocabolario

Nel vocabolario iniziale erano presenti parole come:

- `jeans`
- `share`
- `shake`
- `smoke`
- `white`

Queste parole erano troppo poco integrate per il criterio richiesto.

### 2. `jeans` presente anche tra le soluzioni

`jeans` compariva nelle soluzioni, quindi poteva uscire come parola da indovinare. Questo era contrario alla richiesta.

### 3. Overflow orizzontale su mobile

La tastiera, in viewport stretta, usciva leggermente dai bordi.

## Modifiche fatte

### Modifiche a `build.py`

Sono state aggiunte regole per distinguere:

- forestierismi comuni da mantenere
- prestiti stabili ormai accettabili
- forestierismi da escludere

Nuove parti introdotte:

- set `FORESTIERISMI_COMUNI`
- set `PRESTITI_STABILI`
- set `FORESTIERISMI_DA_ESCLUDERE`
- funzione `troppo_forestiera(p)`
- funzione `screma_tentativi(parole, log)`

È stata inoltre aggiunta la rimozione di `jeans` dalla scrematura soluzioni.

### Modifiche al flusso di build

La build ora:

- filtra le soluzioni
- screma qualitativamente le soluzioni
- screma anche i tentativi dai forestierismi troppo forzati
- rigenera HTML, liste e log aggiornati

### Modifiche responsive alla GUI

Nel template CSS generato da `build.py` è stato aggiunto un blocco `@media (max-width: 420px)` per:

- ridurre padding della tastiera
- ridurre gap tra i tasti
- abbassare leggermente l'altezza dei tasti
- permettere ai tasti di comprimersi meglio
- eliminare l'overflow laterale su mobile

## Risultato attuale del vocabolario

### Soluzioni

- prima: `1369`
- attuale: `1368`

`jeans` è stato rimosso dalle soluzioni.

### Tentativi

- prima: `7827`
- attuale: `7801`

Sono stati rimossi 26 tentativi troppo poco integrati, tra cui:

- `jeans`
- `ebook`
- `share`
- `shake`
- `smoke`
- `white`
- `skate`
- `spike`
- `trans`

### Parole mantenute perché considerate accettabili

Restano accettate parole come:

- `sport`
- `karma`
- `koala`
- `virus`
- `clown`
- `hobby`
- `relax`

## Stato dei test dopo le modifiche

Esito finale dei test automatizzati:

- GUI desktop: ok
- GUI mobile: ok
- tastiera fisica: ok
- tastiera virtuale: ok
- controllo parola non valida: ok
- `jeans` rifiutata come tentativo: ok
- vittoria e modale finale: ok
- statistiche: ok
- nuova partita: ok
- overflow mobile: risolto

## File aggiornati finora

- `build.py`
- `parole-infinito.html`
- `parole_soluzioni.txt`
- `parole_tentativi.txt`
- `build_log.md`

## Stato attuale

Il progetto è in stato funzionante.

Attualmente il gioco:

- gira correttamente in browser
- usa liste rigenerate
- esclude inglesismi troppo forzati come `jeans`
- mantiene invece parole ormai comuni come `sport`
- ha una GUI verificata anche su mobile

## Compatibilita' Ubuntu

Verifica eseguita su Ubuntu il `2026-04-05`.

Esito:

- `python3 -m py_compile build.py serve_local.py report_playtest.py`: ok
- `python3 build.py`: ok
- `python3 serve_local.py --host 127.0.0.1 --port 8011`: ok
- `GET /parole-infinito.html`: HTTP `200`
- `POST /api/attempt`: HTTP `204`
- `python3 report_playtest.py`: ok

Note pratiche per Ubuntu:

- il progetto funziona con `python3`, senza dipendenze extra da installare con `pip`
- `sqlite3` come libreria Python e' gia' usata correttamente anche se il client CLI `sqlite3` non e' installato
- il file `tools/cloudflared.exe` e' un binario Windows e non serve per eseguire il progetto in locale su Ubuntu
- se serve un tunnel pubblico su Ubuntu, conviene installare la versione Linux di `cloudflared` separatamente invece di usare `tools/cloudflared.exe`

## Monitoraggio modifiche e log

Da ora il progetto usa questa struttura di monitoraggio:

- `CHANGELOG.md`: da aggiornare quando cambiano logica, regole, GUI o criteri linguistici
- `build_log.md`: ultimo log completo della build
- `build_history.md`: storico sintetico cumulativo delle build
- `stato_progetto.md`: riepilogo generale del progetto e del suo stato

Uso consigliato:

- quando si cambia il codice: aggiornare `CHANGELOG.md`
- quando si rigenera il gioco: eseguire `python3 build.py`
- dopo la build: controllare `build_log.md` e `build_history.md`

## Possibili miglioramenti futuri

- fare una scrematura ancora più severa delle soluzioni borderline
- rivedere manualmente alcuni prestiti rimasti tra le soluzioni
- aggiungere un file di criteri linguistici per governare meglio le esclusioni future

## Aggiornamento revisione - 26/03/2026

### Nuova verifica sulla difficoltà

È stata fatta una revisione ulteriore del bilanciamento del gioco con questo obiettivo:

- rendere `Parole Infinito` più adatto a essere giocato da persone diverse
- mantenere i `6 tentativi` come nel gioco originale
- non allargare ulteriormente i tentativi, ma rendere più eque le `soluzioni`

Esito della verifica:

- il problema principale non è il numero di tentativi accettati
- la distinzione tra `soluzioni` e `tentativi` è già corretta
- la difficoltà percepita dipende soprattutto da alcune parole presenti tra le `soluzioni`
- in particolare pesano:
  - forme verbali coniugate come soluzione
  - parole con lettere ripetute o doppie molto punitive
  - famiglie troppo ambigue con molte alternative simili

### Verifica rispetto al progetto originale di pietroppeter

È stato verificato direttamente il file `curated.txt` del progetto originale `pietroppeter/wordle-it`.

Risultato:

- alcune forme verbali al presente che sembrano dure sono davvero presenti anche nell'originale
- esempi confermati presenti nel file originale:
  - `hanno`
  - `vanno`
  - `vuole`
  - `vieni`
  - `vinco`
  - `valgo`
  - `tengo`

Conclusione:

- queste parole non sono "errori" rispetto all'originale
- però il progetto attuale non deve per forza replicare in modo identico tutta la filosofia della lista originale
- se l'obiettivo è un browser game più accessibile e più gradevole da giocare in sequenza, ha senso fare una selezione soluzioni più "fair"

## Aggiornamento modalità giornaliera - 26/03/2026

### Richiesta

Richiesta ricevuta:

> "aggiungi la modalità giornaliera per ora, e spiegami come si potrebbe fare per creare appunto una sorta di classifica, in più il messaggio in chat non è abbastanza dato che può facilmente essere falsato"

### Decisioni progettuali adottate

Per la modalità giornaliera sono state prese queste decisioni:

- mantenere la modalità infinita esistente
- aggiungere una modalità `24H` con una parola del giorno uguale per tutti
- usare la data locale del browser come riferimento della sfida giornaliera
- rendere la parola giornaliera deterministica a partire da una data base fissa
- salvare stato e statistiche della modalità giornaliera separatamente da quelle infinite
- impedire il reroll della parola giornaliera: dal popup finale il bottone principale porta alla modalità infinita, non a una nuova daily

### Motivo delle scelte

La modalità giornaliera serve come base per una futura classifica.

Se la daily potesse essere rigenerata liberamente o non conservasse il progresso, non sarebbe adatta a confronti tra amici.

La separazione tra:

- `infinita`
- `giornaliera`

permette invece di avere:

- una modalità casuale per giocare liberamente
- una modalità comune e confrontabile per tutti

### Modifiche implementate

Nel template del gioco sono state aggiunte:

- badge modalità nel logo
- pulsante `24H` / `∞` nell'header per cambiare modalità
- generazione deterministica della parola del giorno
- persistenza `localStorage` separata per stato e statistiche delle due modalità
- condivisione diversa per la modalità giornaliera, con ID sfida del giorno nel messaggio
- testo help aggiornato per spiegare le due modalità
- correzione del contatore locale della modalità infinita per evitare che la prima partita parta da `2` dopo un passaggio iniziale dalla daily

### Formato attuale della condivisione

La modalità giornaliera ora usa un formato del tipo:

- `Par🇮🇹le #N 3/6`

seguito dalla griglia emoji.

Questo è migliore del numero partita locale della modalità infinita, ma non è ancora un sistema anti-cheat.

### Valutazione anti-falsificazione

È stato confermato che un semplice messaggio copiato in chat:

- è utile per condividere il risultato
- ma può essere falsificato facilmente

Quindi da solo non può essere considerato una classifica affidabile.

### Strada consigliata per una classifica vera

Per avere una classifica attendibile servono almeno:

- una parola giornaliera uguale per tutti
- un identificatore utente
- un servizio esterno che riceva i risultati
- validazione lato server o lato bot

Soluzione consigliata per il vostro uso con Telegram:

- mantenere la modalità giornaliera nel gioco
- creare un bot Telegram
- far inviare il risultato al bot dal gioco o tramite comando
- far validare al bot giorno, tentativi e sequenza guess
- far pubblicare al bot la classifica del giorno nel gruppo

### Nota tecnica sulla validazione

Per evitare falsificazioni reali, il bot o backend non deve fidarsi del solo testo condiviso.

Serve almeno uno di questi approcci:

- invio della sequenza completa dei tentativi e verifica contro la parola del giorno
- invio a backend del risultato direttamente dal gioco
- token/sessione firmata dal server prima di giocare e verificata al submit

La soluzione più semplice ma abbastanza solida è:

- backend con parola del giorno nota solo al server
- submit dei guess finali
- controllo server-side
- aggiornamento leaderboard

### Stato della verifica

È stata eseguita con successo una nuova build con `python build.py`.

Controlli eseguiti:

- build completata senza errori
- `dist/parole-infinito.html` rigenerato
- presenza del bottone `btn-mode`
- presenza delle nuove chiavi `parole_mode`, `parole_daily_state`, `parole_daily_stats`
- controllo di sintassi del blocco JavaScript finale con `node`

Limite attuale della verifica:

- in questo ambiente non è stato possibile completare un test browser headless reale con Playwright già pronto come modulo Node
- quindi la verifica finale della UI è stata fatta a livello di build e consistenza del file generato, non con un click-through automatizzato completo

## Nota tecnica daily condivisa - 26/03/2026

Osservazione emersa nel test reale:

> due persone hanno visto parole diverse in modalità `24H`

Chiarimento tecnico:

La modalità giornaliera implementata lato client può produrre la stessa parola per tutti solo se sono uguali contemporaneamente:

- build del gioco
- ordine della lista `SOLUZIONI`
- data locale usata dal browser
- fuso orario o ora di sistema percepita dal dispositivo

Quindi il fatto che il gioco sia "in locale" non è di per sé il problema.

Il vero problema è che, senza una fonte centrale condivisa, due persone possono facilmente avere:

- copie diverse del file HTML
- build diverse rigenerate in momenti diversi
- orologio locale non allineato
- cache o file vecchi

Conclusione pratica:

- la daily attuale è utile come base UX e come prototipo
- ma non è ancora una daily centralizzata e garantita
- per avere davvero la stessa parola per tutti serve una sorgente unica comune

Le due strade corrette sono:

- pubblicare una singola build online e fare in modo che tutti usino quella stessa build
- oppure, meglio, far arrivare `day_id` e parola del giorno da un backend o da un file remoto condiviso

Per una classifica affidabile la seconda strada resta comunque la migliore.

## Aggiornamento test sharing locale - 26/03/2026

Decisione operativa concordata:

- prima fase: test del gioco, del vocabolario e della UX
- niente Telegram o leaderboard per ora
- condivisione tramite host statico dal PC con link da inoltrare

### Implementazione fatta

È stato aggiunto lo script:

- `serve_local.py`

Scopo:

- servire la cartella `dist/` in HTTP locale
- permettere di aprire il gioco da altri dispositivi sulla stessa rete
- usare un link stabile invece di mandare il solo file HTML

### Comando previsto

Avvio locale:

- `python serve_local.py --port 8000`

Lo script stampa:

- URL locale per il PC
- URL di rete locale da aprire da telefono o altri computer

### Limiti dichiarati

Questa soluzione è adatta per:

- playtest con amici
- raccolta feedback sul vocabolario
- controllo UX reale su dispositivi diversi

Non è adatta da sola per:

- daily centralizzata affidabile
- classifica verificata
- condivisione fuori dalla rete locale senza passaggi aggiuntivi su router o tunnel

## Aggiornamento tunnel temporaneo - 26/03/2026

Nuova esigenza emersa:

- condividere il gioco con poche persone anche fuori dalla rete locale

Soluzione adottata per il playtest:

- quick tunnel temporaneo con `cloudflared`

### Motivo della scelta

Per un gruppo molto piccolo di tester questa soluzione è la più rapida perché:

- non richiede deploy pubblico stabile
- non richiede configurazione router
- non richiede Telegram bot o backend
- espone direttamente il server locale già acceso sulla porta `8000`

### Stato tecnico

Azioni eseguite:

- scaricato `cloudflared.exe` nella cartella `tools/`
- avviato tunnel temporaneo verso `http://127.0.0.1:8000`
- verificata raggiungibilità pubblica della pagina `parole-infinito.html` con risposta HTTP `200`

### Limiti

Questo tunnel è adatto solo per test:

- URL temporaneo
- dipende dal PC acceso
- dipende sia dal server locale sia dal processo `cloudflared`
- non è base sufficiente per daily affidabile o classifica

## Aggiornamento monitoraggio playtest - 27/03/2026

Nuova richiesta:

- tracciare tentativi e soluzioni provati dai tester senza perdere dati durante il playtest remoto
- mantenere lo stesso link pubblico già distribuito

### Strategia adottata

Per non cambiare il link del tunnel è stato lasciato attivo `cloudflared` e sostituito solo il server locale sulla stessa porta `8000`.

Dato che il tunnel continua a puntare a `127.0.0.1:8000`, il link pubblico resta invariato anche se il server locale viene riavviato.

### Modifiche applicate

È stato aggiornato `serve_local.py` per diventare un piccolo server di playtest con:

- serving statico della cartella `dist/`
- endpoint `POST /api/attempt`
- inizializzazione automatica del database SQLite

È stato inoltre aggiornato `template_parole.html` per inviare eventi di telemetria al backend:

- `accepted_guess` per i tentativi validati dal gioco
- `rejected_guess` per parole da 5 lettere rifiutate dal dizionario
- `game_end` a fine partita

### Database usato

Percorso:

- `data/playtest.db`

Tabella:

- `playtest_events`

Campi principali registrati:

- tipo evento
- sessione
- client
- modalità
- challenge id
- numero tentativo
- guess
- pattern risultato
- soluzione
- esito finale
- IP remoto
- user agent

### Stato della verifica

Verifiche eseguite con esito positivo:

- build rigenerata
- sintassi JS verificata
- sintassi Python del server verificata
- server locale riavviato sulla porta `8000`
- tunnel pubblico rimasto raggiungibile con risposta HTTP `200`
- insert di prova eseguito su `playtest.db`

### Limite noto

Il monitoraggio registra i guess confermati dal gioco e i guess rifiutati dal dizionario, non ogni singola digitazione parziale sulla tastiera.

## Fix popup fine partita dopo refresh - 27/03/2026

Problema segnalato da playtest reale via video:

- la partita risultava finita
- la modale finale scompariva
- dopo il refresh non riappariva
- l'utente restava bloccato senza poter avviare una nuova partita

### Causa individuata

Lo stato della partita finita veniva salvato correttamente, ma in fase di ripristino:

- la griglia veniva ricostruita
- la tastiera veniva ricostruita
- la modale finale veniva sempre chiusa

quindi la pagina si riapriva in stato `finita = true` ma senza popup visibile.

### Correzione applicata

È stata introdotta una funzione di render della modale finale e il ripristino ora fa questo:

- se la partita non è finita, ripristina solo griglia e tastiera
- se la partita è finita, ricostruisce anche il contenuto della modale
- riapre automaticamente la modale al refresh

### Effetto atteso

Dopo un refresh di una partita già conclusa:

- il popup finale deve ricomparire
- il giocatore deve poter usare di nuovo il pulsante per la nuova partita

### Stato verifica

- build rigenerata senza interrompere tunnel o link pubblico
- funzione di render della modale presente nella build finale
- richiamo di riapertura della modale presente nel ripristino stato

## Fix formattazione modale finale - 27/03/2026

Nuovo feedback da screenshot di playtest:

- il popup finale era di nuovo visibile dopo il refresh
- ma alcuni testi e le righe emoji apparivano corrotti
- il problema era visibile nel popup, mentre il testo copiato negli appunti risultava corretto

### Causa individuata

La nuova funzione introdotta per ricostruire il popup finale conteneva stringhe con encoding corrotto.

Questo impattava:

- titoli con emoji
- stato "fine partita"
- griglia emoji renderizzata nella modale

La funzione di condivisione invece usava un altro codice e quindi restava corretta.

### Correzione applicata

È stato aggiunto un override pulito di `renderFinePartita` usando escape Unicode espliciti, per evitare nuovi problemi di encoding nel file HTML generato.

### Stato verifica

- build rigenerata senza cambiare il link pubblico
- pagina pubblica ancora raggiungibile con risposta HTTP `200`
- il fix è presente nel file finale servito dal tunnel

### Decisione condivisa sui verbi

Decisione attuale concordata:

- le forme verbali coniugate al presente possono restare tra le `soluzioni`
- i tempi più complessi o meno naturali da indovinare devono restare al massimo nei `tentativi`
- esempi da escludere come `soluzioni`:
  - passati remoti
  - condizionali
  - congiuntivi
  - imperfetti
  - forme verbali poco trasparenti o rare nel parlato

Questo significa che la regola futura non sarà:

- "niente verbi tra le soluzioni"

ma sarà:

- "presenti semplici e naturali ammessi"
- "forme verbali complesse o punitive escluse dalle soluzioni"

### Proposta criteri per la prossima scrematura soluzioni

Per mantenere il gioco a `6 tentativi` senza renderlo frustrante, i criteri proposti sono:

- tenere i `tentativi` ampi e permissivi, molto vicini allo stato attuale
- restringere le `soluzioni` a parole più quotidiane e più leggibili

Criteri proposti per le `soluzioni`:

- mantenere:
  - sostantivi e aggettivi comuni
  - forme verbali al presente molto naturali e trasparenti
  - parole riconoscibili da un giocatore medio senza conoscenze tecniche

- escludere dalle `soluzioni` ma tenere nei `tentativi`:
  - passati remoti in `-ai` e `-ii`
  - condizionali tipo `-rei`
  - imperfetti tipo `-avo`, `-iva`
  - congiuntivi e forme verbali poco intuitive
  - parole troppo tecniche, arcaiche o letterarie
  - parole molto punitive con doppie o ripetizioni, se non davvero comuni
  - cluster troppo affollati di parole quasi indistinguibili

### Indicazione di bilanciamento attuale

Direzione consigliata per la prossima iterazione:

- mantenere `6 tentativi`
- non toccare la lista `tentativi` se non in casi evidenti
- ridurre la durezza media delle `soluzioni`
- portare le `soluzioni` verso un insieme più adatto a un pubblico generale

### Nota operativa richiesta dall'utente

Richiesta esplicita da seguire da ora in poi:

- ogni ragionamento importante
- ogni decisione di progetto
- ogni cambiamento o modifica

devono essere riportati e aggiornati anche in questo file `stato_progetto.md`

## Aggiornamento implementazione - 26/03/2026

### Intervento eseguito

Su richiesta dell'utente il progetto e' stato modificato, rigenerato e ripulito.

Obiettivi applicati:

- mantenere `6 tentativi`
- rendere le `soluzioni` piu' fair
- eliminare versioni vecchie e file non piu' necessari
- riorganizzare il progetto in una struttura piu' chiara

### Nuova struttura cartelle

Struttura finale attiva:

- `build.py`: generatore principale del progetto
- `src/template_parole.html`: template HTML di base del gioco
- `dist/parole-infinito.html`: build finale giocabile
- `dist/parole_soluzioni.txt`: soluzioni finali
- `dist/parole_tentativi.txt`: tentativi finali
- `docs/build_log.md`: log ultimo build
- `docs/build_history.md`: storico build
- `docs/CHANGELOG.md`: changelog progetto
- `docs/stato_progetto.md`: stato progetto e decisioni

Sono state eliminate le vecchie cartelle di lavoro:

- `prova1`
- `prova2`

### Cambiamenti di logica applicati

Nel nuovo `build.py` sono state introdotte queste regole:

- i presenti semplici ammessi possono restare tra le `soluzioni`
- passati remoti, forme in `-ii`, condizionali e imperfetti vengono esclusi dalle `soluzioni`
- forme presenti considerate poco naturali come answer vengono rimosse
- parole tecniche, arcaiche o borderline vengono rimosse dalle `soluzioni`
- i cluster troppo ambigui con doppie o troppe alternative vicine vengono rimossi dalle `soluzioni`
- i `tentativi` restano larghi e permissivi, con scrematura limitata ai forestierismi poco integrati

### Effetto sul vocabolario

Dopo il rebalance:

- soluzioni iniziali valide: `1523`
- soluzioni finali: `1329`
- tentativi iniziali validi: `7827`
- tentativi finali: `7800`

Esempi rimossi dalle `soluzioni`:

- forme punitive o poco naturali: `annoi`, `berci`, `cadde`
- cluster duri: `detto`, `tetto`, `cassa`
- tempi verbali complessi: molti passati remoti in `-ai` e `-ii`

Esempi mantenuti tra le `soluzioni` per coerenza con la decisione presa:

- `hanno`
- `vanno`
- `vieni`
- `tengo`
- `valgo`
- `vinco`
- `vuole`

### Verifica finale eseguita

Verifiche fatte dopo la nuova build:

- build eseguita con successo da `build.py`
- file finali generati correttamente in `dist/`
- vocabolario HTML aggiornato correttamente senza duplicazioni
- screenshot della UI finale eseguito con browser headless per verificare che il layout non si fosse rotto
- analisi quantitativa del nuovo set soluzioni

Esito della verifica quantitativa:

- media solver: `3.385`
- distribuzione solver:
  - `2` tentativi: `68`
  - `3` tentativi: `713`
  - `4` tentativi: `516`
  - `5` tentativi: `32`
- soluzioni con lettere ripetute: `655` su `1329`

Confronto qualitativo rispetto alla build precedente:

- ridotti diversi outlier frustranti
- ridotti cluster molto punitivi con doppie
- mantenuta la filosofia dei `6 tentativi`

### Stato attuale reale

Il progetto e' ora in uno stato piu' ordinato e piu' adatto a essere condiviso:

- struttura cartelle pulita
- build unica e leggibile
- vecchie versioni rimosse
- dizionario soluzioni riequilibrato
- gioco finale pronto in `dist/parole-infinito.html`

## Aggiornamento share e nuove esclusioni - 26/03/2026

### Nuovo feedback utente recepito

Dopo una sessione di gioco reale l'utente ha segnalato:

- presenza di parole ancora troppo poco comuni come `biada`
- dubbio sul tenere `sport` come soluzione
- assenza di una vera funzione di condivisione del risultato
- interesse per una classifica o collegamento con gli amici, in particolare via Telegram

### Modifiche applicate

Sono state fatte due modifiche immediate al progetto:

- `biada` rimossa dalle `soluzioni`
- `sport` rimossa dalle `soluzioni`

Entrambe restano valide come `tentativi`.

Inoltre e' stata aggiunta la condivisione del risultato nella modale finale:

- nuovo pulsante `Condividi`
- copia automatica negli appunti
- formato messaggio stile:
  - `Par🇮🇹le <numero> <risultato>/6`
  - righe emoji della partita

Esempio del formato implementato:

- `Par🇮🇹le 1543 3/6`
- griglia emoji sotto

### Stato del vocabolario dopo l'ultimo intervento

Nuovi numeri:

- soluzioni finali: `1327`
- tentativi finali: `7800`

Verifica esplicita finale:

- `biada`: non piu' presente tra le soluzioni
- `sport`: non piu' presente tra le soluzioni
- `hanno`, `vanno`, `vieni`, `tengo`: ancora presenti tra le soluzioni

### Nota sulla classifica con amici

Valutazione tecnica attuale:

- la condivisione del testo copiato ora e' possibile
- una vera classifica tra amici non puo' essere affidabile se ogni partita e' casuale locale
- per avere confronto reale tra amici serve una parola condivisa

La soluzione tecnicamente piu' sensata sarebbe aggiungere una modalita' giornaliera:

- stessa parola per tutti in base alla data
- stessa stringa condivisibile in chat
- poi eventuale classifica Telegram o in-app

Senza una modalita' giornaliera condivisa, una classifica avrebbe poco senso perche' ognuno starebbe giocando parole diverse
## 2026-03-28 - Analisi log playtest e nuovo rebalance soluzioni

### Analisi dei log raccolti

Dai log di `data/playtest.db` e dal report playtest emergono tre segnali utili:

- il problema principale non e' il numero di tentativi, ma la qualita' percepita di alcune `soluzioni`
- alcune parole risultano corrette ma poco evocabili come risposta finale (`bidet`, `cruna`, `biada`, `bitta`, `sport`, `torba`)
- alcune parole difficili ma difendibili (`acume`, `gamma`) possono restare nelle soluzioni, ma non devono uscire troppo spesso

Fotografia del campione analizzato al momento della modifica:

- eventi totali: `286`
- partite concluse: `40`
- partite vinte: `35`
- partite perse: `5`
- media tentativi nelle vittorie: `4.43`

Parole emerse come critiche tra feedback diretto e log:

- segnalate dall'utente: `bidet`, `cruna`, `biada`, `bitta`, `sport`, `torba`
- parole perse almeno una volta nei log: `largo`, `bitta`, `bulbo`, `punge`, `tonno`

### Decisione progettuale applicata

E' stata adottata una logica a difficolta' pesata per le `soluzioni`:

- `facili`: piu' frequenti come estrazione
- `medie`: frequenza intermedia
- `difficili`: presenti ma piu' rare

Obiettivo:

- evitare che il gioco si impoverisca troppo
- lasciare in rotazione parole difficili ma accettabili
- ridurre la frequenza delle parole fredde o poco naturali come soluzione

### Modifiche applicate al vocabolario

Rimosse dalle `soluzioni` ma lasciate valide come `tentativi`:

- `bidet`
- `cruna`
- `biada`
- `bitta`
- `sport`
- `torba`

Mantenute nelle `soluzioni`, ma marcate come difficili e quindi meno frequenti:

- `acume`
- `gamma`

E' stata inoltre introdotta una lista manuale di parole difficili che restano possibili ma non dominano le estrazioni.

### Modifiche applicate alla logica del gioco

- la modalita' iniziale di default ora e' `24H`
- se la daily del giorno e' gia' conclusa, alla chiusura della modale finale il gioco passa automaticamente alla modalita' infinita
- lo switch `24H / ∞` resta disponibile per cambiare modalita' manualmente

### Modifiche UI mobile

- aumentata leggermente l'altezza dei tasti della tastiera mobile
- aumentato il padding inferiore della tastiera per alzarla su dispositivi dove risultava troppo bassa
- aggiunta compatibilita' con `safe-area-inset-bottom`

### Verificato

- `python build.py` eseguito con successo
- build finale aggiornata in `dist/parole-infinito.html`
- presenza nella build finale di:
  - `SOLUZIONI_FACILI`
  - `SOLUZIONI_MEDIE`
  - `SOLUZIONI_DIFFICILI`
  - `modalitaIniziale()`
  - `scegliSoluzioneCasuale()`
  - `parolaGiornaliera()`
  - `modalitaDopoChiusura`
- verifica puntuale del vocabolario:
  - `bidet`, `cruna`, `biada`, `bitta`, `sport`, `torba` non sono piu' nelle `soluzioni`
  - restano presenti nei `tentativi`
  - `acume` e `gamma` restano presenti nelle `soluzioni`

### Nota operativa

Per il prossimo passaggio conviene continuare con feedback reali:

- raccogliere altre parole percepite come innaturali
- evitare tagli massivi alla cieca
- usare i log solo come supporto, non come criterio unico
