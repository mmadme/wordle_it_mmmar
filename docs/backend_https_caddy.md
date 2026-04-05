# Backend HTTPS - Caddy

Questa guida prepara il backend `woordle_new_github` per essere esposto in HTTPS usando Caddy come reverse proxy.

Obiettivo:

- ottenere un backend raggiungibile in HTTPS
- mantenere il processo Python su una porta interna
- rendere il backend compatibile con un frontend pubblicato su GitHub Pages

## Perche' serve questa fase

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

- `sborraparle.duckdns.org`

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
- `sborraparle.duckdns.org` che risolve verso la VPS

## File preparati nel progetto

- `deploy/caddy/Caddyfile.example`

## Configurazione Caddy prevista

Configurazione minimale adottata per questa VPS:

```caddy
sborraparle.duckdns.org {
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
curl -I --resolve sborraparle.duckdns.org:80:127.0.0.1 http://sborraparle.duckdns.org
```

Risultato atteso:

- `HTTP/1.1 308 Permanent Redirect`
- `Location: https://sborraparle.duckdns.org/`

### 6. Verificare HTTPS pubblico

```bash
curl -I https://sborraparle.duckdns.org
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

Blocco attuale:

- Let\'s Encrypt fallisce il challenge con:

```text
92.4.220.150: Timeout during connect (likely firewall problem)
```

Interpretazione pratica:

- la VM ascolta correttamente su `80/443`
- `iptables` locale consente `80/443`
- manca ancora raggiungibilita' pubblica effettiva su `80` e/o `443` dal lato Oracle Cloud

## Cosa controllare su Oracle Cloud

Verificare nella VCN/subnet dell'istanza:

- regola ingress TCP `80` da `0.0.0.0/0`
- regola ingress TCP `443` da `0.0.0.0/0`
- se l'istanza usa un NSG, le stesse regole devono essere presenti anche li'
- la VNIC dell'istanza deve avere Public IPv4 attivo

Finche' questo blocco non e' risolto, Caddy continuera' a ritentare l'emissione del certificato ma GitHub Pages restera' bloccato dal mixed content

## CORS dopo GitHub Pages

Quando avremo l'URL reale del frontend GitHub Pages, conviene restringere il backend:

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

Quando HTTPS backend sara' attivo, il frontend Pages andra' rigenerato con:

```bash
python3 build_github_pages.py --api-base https://sborraparle.duckdns.org
```

Questo produrra' un `github_pages/api-config.js` coerente con il backend finale.

## Checklist

- [x] Caddy installato
- [ ] porte `80` e `443` pubblicamente raggiungibili
- [x] `/etc/caddy/Caddyfile` installato
- [x] `caddy validate` ok
- [x] `systemctl restart caddy` ok
- [x] redirect HTTP locale verificato
- [ ] backend raggiungibile in HTTPS
- [ ] frontend GitHub Pages rigenerato con API base `https://sborraparle.duckdns.org`
