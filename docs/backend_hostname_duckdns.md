# Backend Hostname - DuckDNS

Questa guida serve per ottenere e mantenere un hostname stabile gratuito per il backend VPS usando DuckDNS.

Obiettivo:

- avere un nome fisso al posto dell'IP pubblico
- esempio finale: `mionome.duckdns.org`
- usare quel nome come base DNS del backend API della architettura ibrida

## Cosa risolve e cosa non risolve

DuckDNS risolve:

- hostname pubblico stabile
- aggiornamento semplice dell'IP se cambia
- costo zero

DuckDNS da solo non risolve:

- terminazione HTTPS del backend applicativo
- rimozione automatica della porta `:8015` lato frontend finale
- eventuali blocchi mixed content se il frontend usa HTTPS e il backend resta in HTTP

Per GitHub Pages, questa guida va letta come:

- passo utile per avere un hostname stabile
- base DNS della soluzione finale, completata poi da Caddy e HTTPS

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

Nel flusso finale consigliato:

- il backend Python continua ad ascoltare internamente su `8015`
- Caddy espone pubblicamente il backend su `https://woordletest.duckdns.org`

Quindi il frontend GitHub Pages deve puntare a:

```text
https://woordletest.duckdns.org
```

La porta `8015` resta utile solo per test interni o diagnostica locale sulla VPS, per esempio:

```text
http://127.0.0.1:8015/parole-infinito.html
```

## Passo 7 - Aggiornare il frontend GitHub Pages

Quando cambia il dominio backend o si rigenera il pacchetto Pages, va aggiornato:

- `github_pages/api-config.js`

oppure rigenerarlo con:

```bash
python3 build_github_pages.py --api-base https://woordletest.duckdns.org
```

## Nota architetturale finale

GitHub Pages pubblica il frontend in HTTPS.

Per questo motivo il frontend finale non dovrebbe puntare al backend in HTTP su `:8015`, anche se DuckDNS risolve correttamente.

Tradotto:

- DuckDNS risolve il DNS dinamico
- Caddy risolve HTTPS e reverse proxy pubblico
- il backend Python su `8015` resta un dettaglio interno dell'infrastruttura

## Checklist pratica

- [ ] sottodominio creato su DuckDNS
- [ ] token recuperato
- [ ] `duckdns/duckdns.env` compilato
- [ ] `./duckdns/update_duckdns.sh` eseguito con esito `OK`
- [ ] hostname DuckDNS risolve verso la VPS
- [ ] cron configurato
- [ ] backend raggiungibile in HTTPS tramite hostname fisso

## Riferimenti ufficiali

- DuckDNS install linux/cron: https://www.duckdns.org/install.jsp?tab=linux-cron
