# Backend HTTPS - Caddy

Questa guida documenta come il backend `woordle_new_github` viene esposto in HTTPS usando Caddy come reverse proxy.

Obiettivo:

- ottenere un backend raggiungibile in HTTPS
- mantenere il processo Python su una porta interna
- rendere il backend compatibile con un frontend pubblicato su GitHub Pages

## Perche' serve

GitHub Pages pubblica il frontend in HTTPS.

Se il frontend in HTTPS prova a chiamare un backend in HTTP, il browser puo' bloccare la richiesta per mixed content.

Quindi:

- hostname stabile da solo non basta
- per la variante GitHub Pages serve quasi certamente HTTPS sul backend

## Strategia scelta

Scelta consigliata:

- backend Python su `127.0.0.1:8015`
- Caddy esposto pubblicamente su `80` e `443`
- Caddy fa da reverse proxy verso `127.0.0.1:8015`
- certificato TLS gestito automaticamente da Caddy

Dominio previsto:

- `backend.example.com`

## Riferimenti ufficiali

- Caddy install: https://caddyserver.com/docs/install
- Caddy HTTPS quick-start: https://caddyserver.com/docs/quick-starts/https
- Caddy reverse_proxy: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy

## Prerequisiti

- DuckDNS gia' funzionante
- backend test gia' funzionante su `8015`
- porte `80` e `443` aperte:
  - su Oracle Cloud
  - nel firewall della VM
- hostname backend che risolve verso la VPS

Nota:

- le Security List OCI da sole non bastano
- se la VM ha `iptables` con `REJECT` finale e senza `ACCEPT` per `80/443`, il dominio risolve ma i client esterni vedono timeout

## File preparati nel progetto

- `deploy/caddy/Caddyfile.example`

## Configurazione Caddy prevista

Configurazione minimale adottata per questa VPS:

```caddy
backend.example.com {
	reverse_proxy 127.0.0.1:8015
}
```

Nel progetto e' disponibile qui:

- `deploy/caddy/Caddyfile.example`

## Installazione consigliata su Ubuntu

Il team Caddy raccomanda i pacchetti ufficiali per Debian/Ubuntu.

Comandi da usare:

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

## Configurazione pratica

### 1. Creare la directory Caddy dedicata

```bash
sudo mkdir -p /etc/caddy
```

### 2. Installare il Caddyfile

```bash
sudo cp /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github/deploy/caddy/Caddyfile.example /etc/caddy/Caddyfile
```

### 3. Validare la configurazione

```bash
sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
```

### 4. Riavviare Caddy

```bash
sudo systemctl restart caddy
sudo systemctl status caddy
```

### 5. Verificare HTTP locale e redirect

Verifica minima eseguita con successo su questa VPS:

```bash
curl -I --resolve <backend-domain>:80:127.0.0.1 http://<backend-domain>
```

Risultato atteso:

- `HTTP/1.1 308 Permanent Redirect`
- `Location: https://<backend-domain>/`

### 6. Verificare HTTPS pubblico

```bash
curl -I https://<backend-domain>
```

Nota:

- il certificato viene emesso solo se Let's Encrypt riesce a raggiungere pubblicamente `80` e `443`
- se il comando va in timeout o il certificato non viene emesso, il problema e' quasi certamente fuori dalla VM

## Stato reale attuale

Questa parte e' gia' stata verificata:

- `caddy` installato correttamente
- `caddy validate` ok
- `caddy.service` attivo
- listener locali presenti su `*:80` e `*:443`
- redirect HTTP locale verificato con `308`
- reverse proxy verso `127.0.0.1:8015` configurato
- backend pubblico servito in HTTPS tramite Caddy
- frontend GitHub Pages configurato per usare un endpoint API HTTPS
- `github_pages/api-config.js` valorizzato con un backend remoto HTTPS reale

## Cosa controllare su Oracle Cloud

Verificare nella VCN/subnet dell'istanza:

- regola ingress TCP `80` da `0.0.0.0/0`
- regola ingress TCP `443` da `0.0.0.0/0`
- se l'istanza usa un NSG, le stesse regole devono essere presenti anche li'
- la VNIC dell'istanza deve avere Public IPv4 attivo

Questi controlli restano utili come diagnosi se HTTPS smette di funzionare dopo modifiche DNS, firewall o reboot infrastrutturali.

## Firewall locale della VM

Su questa variante il blocco piu' insidioso e' stato proprio qui: OCI aveva `80/443` aperte, Caddy ascoltava su `*:443`, ma la VM rifiutava comunque il traffico perche' `iptables` non aveva regole `ACCEPT` esplicite per `80` e `443`.

Controlli minimi:

```bash
sudo ss -ltnp | grep ':443'
sudo iptables -L INPUT -n --line-numbers
curl -k --resolve <backend-domain>:443:127.0.0.1 https://<backend-domain>/api/daily
```

Se il `curl --resolve ... 127.0.0.1` funziona ma il client esterno no, il backend e Caddy sono sani e il problema e' di raggiungibilita' pubblica.

Obiettivo finale consigliato:

- pubblico solo `80/443`
- backend Python raggiungibile solo internamente su `127.0.0.1:8015`

## CORS dopo GitHub Pages

Ora che il frontend GitHub Pages e' parte del flusso reale, conviene restringere il backend:

Nel file env del backend:

```bash
BACKEND_ALLOW_ORIGINS=https://<tuo-frontend>.github.io
```

oppure:

```bash
BACKEND_ALLOW_ORIGINS=https://<tuo-dominio-frontend>
```

Poi:

```bash
sudo systemctl restart woordle-backend-test
```

o, se avremo migrato al servizio principale:

```bash
sudo systemctl restart woordle-backend
```

## Aggiornare il frontend GitHub Pages

Se cambia il dominio backend oppure si vuole riallineare il pacchetto Pages, il frontend va rigenerato con:

```bash
python3 build_github_pages.py --api-base https://<backend-domain>
```

Questo produrra' un `github_pages/api-config.js` coerente con il backend finale.

## Checklist

- [x] Caddy installato
- [x] porte `80` e `443` pubblicamente raggiungibili
- [x] `/etc/caddy/Caddyfile` installato
- [x] `caddy validate` ok
- [x] `systemctl restart caddy` ok
- [x] redirect HTTP locale verificato
- [x] backend raggiungibile in HTTPS
- [x] frontend GitHub Pages rigenerato con API base `https://<backend-domain>`
