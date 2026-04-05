# Backend Service - systemd

Questa guida stabilizza il backend `woordle_new_github` sulla VPS Ubuntu usando `systemd`.

Obiettivo:

- backend sempre riavviabile
- restart automatico in caso di crash o reboot
- niente dipendenza da terminale aperto
- configurazione separata dal codice

## File preparati nel progetto

- `run_backend_service.sh`
- `deploy/backend.env.example`
- `deploy/backend-test.env.example`
- `deploy/systemd/woordle-backend.service`
- `deploy/systemd/woordle-backend-test.service`

## Cosa fa questa soluzione

- `run_backend_service.sh` legge la configurazione dal file env
- il servizio `systemd` avvia `serve_local.py`
- `systemd` tiene il processo attivo e lo riavvia se cade
- i log restano consultabili con `journalctl`

## Configurazione consigliata

Per il backend remoto attuale:

- host: `0.0.0.0`
- porta: `8015`
- origine consentita: inizialmente `*` oppure il dominio frontend effettivo

Quando il frontend GitHub Pages sara' online, conviene restringere:

- `BACKEND_ALLOW_ORIGINS=https://<tuo-frontend>.github.io`

oppure, se usi un custom domain:

- `BACKEND_ALLOW_ORIGINS=https://<dominio-frontend>`

## Installazione

### Stato attuale consigliato

Per questa variante GitHub la porta definitiva scelta per il backend e' `8015`.

Stato operativo corrente:

- installare `woordle-backend-test.service`
- usare `8015` come porta definitiva del backend Python
- tenere `woordle-backend-test.service` come servizio attivo finche' non decidiamo se rinominarlo

URL di test atteso:

```text
http://sborraparle.duckdns.org:8015/parole-infinito.html
```

### Installazione del service su porta `8015`

#### 1. Creare il file ambiente di test

```bash
sudo cp /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github/deploy/backend-test.env.example /etc/woordle-backend-test.env
sudo nano /etc/woordle-backend-test.env
```

Contenuto iniziale consigliato:

```bash
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8015
BACKEND_ALLOW_ORIGINS=*
BACKEND_LOG_HTTP=1
BACKEND_BUILD_ON_START=0
```

#### 2. Installare il service file di test

```bash
sudo cp /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github/deploy/systemd/woordle-backend-test.service /etc/systemd/system/woordle-backend-test.service
```

#### 3. Ricaricare systemd

```bash
sudo systemctl daemon-reload
```

#### 4. Abilitare e avviare il servizio di test

```bash
sudo systemctl enable --now woordle-backend-test
```

#### 5. Verificare lo stato

```bash
sudo systemctl status woordle-backend-test
journalctl -u woordle-backend-test -f
```

#### 6. Verificare che ascolti sulla porta giusta

```bash
ss -ltnp | grep 8015
curl -I http://127.0.0.1:8015/parole-infinito.html
curl -I http://sborraparle.duckdns.org:8015/parole-infinito.html
```

#### 7. Se vuoi provarlo da fuori

Ricorda che per accesso esterno serve aprire anche la porta `8015`:

- in Oracle Cloud
- nel firewall della VM

### 1. Creare il file ambiente di sistema

```bash
sudo cp /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github/deploy/backend.env.example /etc/woordle-backend.env
sudo nano /etc/woordle-backend.env
```

Contenuto iniziale consigliato:

```bash
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8015
BACKEND_ALLOW_ORIGINS=*
BACKEND_LOG_HTTP=0
BACKEND_BUILD_ON_START=0
```

### 2. Installare il service file

```bash
sudo cp /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github/deploy/systemd/woordle-backend.service /etc/systemd/system/woordle-backend.service
```

### 3. Rendere eseguibile lo script di avvio

```bash
chmod +x /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github/run_backend_service.sh
```

### 4. Ricaricare systemd

```bash
sudo systemctl daemon-reload
```

### 5. Abilitare e avviare il servizio

```bash
sudo systemctl enable --now woordle-backend
```

### 6. Verificare lo stato

```bash
sudo systemctl status woordle-backend
```

### 7. Consultare i log

```bash
journalctl -u woordle-backend -f
```

## Comandi utili

Restart:

```bash
sudo systemctl restart woordle-backend
```

Stop:

```bash
sudo systemctl stop woordle-backend
```

Start:

```bash
sudo systemctl start woordle-backend
```

Disabilitare all'avvio:

```bash
sudo systemctl disable woordle-backend
```

## Nota importante sul conflitto porte

Se esiste gia' un processo avviato manualmente sulla porta scelta, il servizio `systemd` non partira'.

Prima dell'attivazione conviene controllare:

```bash
ss -ltnp | grep 8015
```

Se trovi un processo Python gia' attivo, fermalo prima di fare:

```bash
sudo systemctl enable --now woordle-backend-test
```

In questo progetto, la porta definitiva scelta per il backend e' `8015`.

## Nota su build e deploy

Di default il servizio non esegue `build.py` a ogni avvio:

- `BACKEND_BUILD_ON_START=0`

Questo e' il comportamento consigliato per produzione leggera, per evitare rebuild involontarie.

Se vuoi forzare una rebuild a ogni avvio:

```bash
BACKEND_BUILD_ON_START=1
```

ma di norma e' meglio rigenerare manualmente e poi riavviare il servizio.

## Checklist

- [ ] `run_backend_service.sh` eseguibile
- [ ] `/etc/woordle-backend-test.env` creato, se usi la porta di test
- [ ] `/etc/systemd/system/woordle-backend-test.service` copiato, se usi la porta di test
- [ ] `/etc/woordle-backend.env` creato, se in futuro userai anche il service principale
- [ ] `/etc/systemd/system/woordle-backend.service` copiato, se in futuro userai anche il service principale
- [ ] `systemctl daemon-reload` eseguito
- [ ] `systemctl enable --now woordle-backend-test` eseguito
- [ ] `systemctl status woordle-backend-test` in stato attivo
- [ ] backend raggiungibile su hostname stabile

## Rischio residuo

Questa guida stabilizza il deploy del backend, ma non risolve ancora il tema HTTPS.

Per GitHub Pages, quello restera' il passo successivo piu' importante.
