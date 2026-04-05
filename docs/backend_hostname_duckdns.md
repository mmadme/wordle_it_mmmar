# Backend Hostname - DuckDNS

Questa guida serve per ottenere un hostname stabile gratuito per il backend VPS usando DuckDNS.

Obiettivo:

- avere un nome fisso al posto dell'IP pubblico
- esempio finale: `mionome.duckdns.org`
- usare quel nome per il backend API della futura architettura ibrida

## Cosa risolve e cosa non risolve

DuckDNS risolve:

- hostname pubblico stabile
- aggiornamento semplice dell'IP se cambia
- costo zero

DuckDNS da solo non risolve:

- HTTPS del backend applicativo
- rimozione automatica della porta `:8015`
- eventuali blocchi mixed content se il frontend verra' pubblicato in HTTPS

Per GitHub Pages, questa guida va letta come:

- passo utile per avere un hostname stabile
- non ancora soluzione finale per HTTPS

## Prerequisiti

- VPS Ubuntu gia' funzionante
- backend raggiungibile via IP e porta
- `curl` disponibile
- account DuckDNS

Riferimento ufficiale DuckDNS:

- https://www.duckdns.org/install.jsp?tab=linux-cron

## File preparati nel progetto

Sono stati aggiunti:

- `duckdns/duckdns.env.example`
- `duckdns/update_duckdns.sh`

## Passo 1 - Registrare il sottodominio su DuckDNS

1. Apri `https://www.duckdns.org/`
2. Effettua il login con uno dei provider supportati
3. Crea il sottodominio desiderato, per esempio:
   - `woordletest`
4. Annota:
   - dominio DuckDNS scelto
   - token personale DuckDNS

Risultato atteso:

- hostname finale tipo `woordletest.duckdns.org`

## Passo 2 - Creare la configurazione locale

Dalla cartella del progetto:

```bash
cd /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github
cp duckdns/duckdns.env.example duckdns/duckdns.env
```

Poi modifica `duckdns/duckdns.env` inserendo i valori reali:

```bash
DUCKDNS_DOMAIN=woordletest
DUCKDNS_TOKEN=il-tuo-token-reale
DUCKDNS_IP=
```

Nota:

- lasciare `DUCKDNS_IP` vuoto e' la scelta consigliata

## Passo 3 - Testare l'aggiornamento manuale

```bash
cd /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github
chmod +x duckdns/update_duckdns.sh
./duckdns/update_duckdns.sh
```

Se tutto e' corretto, il comando stampa:

```text
DuckDNS aggiornato: https://<dominio>.duckdns.org
```

e aggiorna:

- `duckdns/duckdns.log`

## Passo 4 - Verificare la risoluzione DNS

```bash
getent hosts woordletest.duckdns.org
```

oppure:

```bash
ping -c 1 woordletest.duckdns.org
```

Il risultato deve puntare all'IP pubblico della VPS.

## Passo 5 - Tenere l'hostname aggiornato nel tempo

DuckDNS consiglia un update periodico, per esempio via cron.

Da terminale:

```bash
crontab -e
```

Aggiungi questa riga:

```bash
*/5 * * * * cd /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github && ./duckdns/update_duckdns.sh >/dev/null 2>&1
```

Verifica:

```bash
crontab -l
```

## Passo 6 - Usare l'hostname con il backend

Finche' il backend resta pubblicato sulla porta `8015`, il link backend sara':

```text
http://woordletest.duckdns.org:8015
```

Per esempio:

```text
http://woordletest.duckdns.org:8015/parole-infinito.html
http://woordletest.duckdns.org:8015/api/attempt
```

## Passo 7 - Aggiornare il frontend GitHub Pages

Quando avremo deciso il valore reale del backend, dovremo aggiornare:

- `github_pages/api-config.js`

oppure rigenerarlo con:

```bash
python3 build_github_pages.py --api-base http://woordletest.duckdns.org:8015
```

## Limite attuale da tenere presente

Se il frontend verra' pubblicato su GitHub Pages, sara' in HTTPS.

Quindi un backend in solo HTTP, anche con hostname DuckDNS stabile, puo' essere bloccato dal browser per mixed content.

Tradotto:

- DuckDNS e' un ottimo passo per la Fase 5
- per la versione finale GitHub Pages servira' quasi certamente anche una Fase HTTPS del backend

## Checklist pratica

- [ ] sottodominio creato su DuckDNS
- [ ] token recuperato
- [ ] `duckdns/duckdns.env` compilato
- [ ] `./duckdns/update_duckdns.sh` eseguito con esito `OK`
- [ ] hostname DuckDNS risolve verso la VPS
- [ ] cron configurato
- [ ] backend raggiungibile con hostname fisso

## Riferimenti ufficiali

- DuckDNS install linux/cron: https://www.duckdns.org/install.jsp?tab=linux-cron
