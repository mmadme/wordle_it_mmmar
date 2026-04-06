# Backend Management

Questa guida raccoglie i comandi pratici per gestire il backend della variante `woordle_new_github` sulla VPS Ubuntu.

Obiettivo:

- tenere il backend sempre acceso in modo affidabile
- capire rapidamente se il servizio e' sano
- controllare log e DB senza dover ricordare ogni volta i comandi sparsi

## Scelta consigliata

Per questo progetto conviene usare:

- `systemd` per il backend Python
- `systemd` per Caddy

Non e' consigliato lasciare il backend aperto in una shell `bash` normale, perche':

- si ferma se chiudi la sessione SSH
- non riparte da solo dopo reboot o crash
- i log sono piu' scomodi da consultare

## Servizi attuali

Backend Python:

- `woordle-backend-test.service`

Reverse proxy HTTPS:

- `caddy.service`

Backend applicativo:

- ascolta internamente su `8015`

Frontend pubblico:

- GitHub Pages gia' attivo

Backend pubblico:

- dietro Caddy su dominio HTTPS dedicato

Nota:

- gli URL pubblici reali non sono riportati in questa guida operativa

## Stato rapido

Per vedere subito se i servizi sono attivi:

```bash
systemctl status woordle-backend-test
systemctl status caddy
```

Se vuoi una versione piu' breve:

```bash
systemctl is-active woordle-backend-test
systemctl is-active caddy
```

Risultato atteso:

- `active`

## Avvio, stop e riavvio

### Riavviare il backend

```bash
sudo systemctl restart woordle-backend-test
```

### Riavviare Caddy

```bash
sudo systemctl restart caddy
```

### Riavviare entrambi

```bash
sudo systemctl restart woordle-backend-test
sudo systemctl restart caddy
```

### Fermare il backend

```bash
sudo systemctl stop woordle-backend-test
```

### Riavviare il backend dopo uno stop

```bash
sudo systemctl start woordle-backend-test
```

## Log del backend

### Vedere gli ultimi log

```bash
journalctl -u woordle-backend-test -n 100 --no-pager
```

### Seguire i log in tempo reale

```bash
journalctl -u woordle-backend-test -f
```

Questo e' il comando piu' utile quando vuoi verificare se il sito GitHub Pages sta davvero inviando i playtest.

Se tutto funziona, vedrai righe del tipo:

```text
OPTIONS /api/attempt -> 204
POST /api/attempt -> 204
```

### Log di Caddy

Per controllare proxy e HTTPS:

```bash
journalctl -u caddy -n 100 --no-pager
```

oppure in tempo reale:

```bash
journalctl -u caddy -f
```

## Verifica HTTP / HTTPS

### Verificare backend locale

```bash
curl -I http://127.0.0.1:8015/parole-infinito.html
```

### Verificare backend pubblico dietro Caddy

```bash
curl -I https://<backend-domain>
```

### Verificare frontend GitHub Pages

```bash
curl -I https://<frontend-domain>/
```

### Verificare la daily ufficiale dal backend

```bash
curl -s https://<backend-domain>/api/daily
```

Valori attesi:

- `daily_no` coerente per tutti i client
- `timezone` uguale a `Europe/Rome`
- `resets_at` valorizzato al prossimo mezzanotte italiana

## Verifica del DB

Il DB reale e':

```text
data/playtest.db
```

### Vedere quante righe ci sono

```bash
cd /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect("data/playtest.db")
print(conn.execute("select count(*) from playtest_events").fetchone()[0])
conn.close()
PY
```

### Vedere gli ultimi eventi registrati

```bash
cd /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect("data/playtest.db")
for row in conn.execute("""
    select id, created_at, event_type, mode, guess, remote_ip
    from playtest_events
    order by id desc
    limit 20
"""):
    print(row)
conn.close()
PY
```

### Rigenerare CSV e report

```bash
cd /home/ubuntu/Desktop/grouphelp/woordleubuntu/woordle_new_github
python3 report_playtest.py
```

File aggiornati:

- `data/playtest_events.csv`
- `docs/playtest_report.md`

## Come diagnosticare se GitHub Pages non scrive nel DB

Sequenza consigliata:

1. apri i log live del backend

```bash
journalctl -u woordle-backend-test -f
```

2. fai `Ctrl+F5` sulla pagina GitHub Pages

3. inserisci un tentativo e premi invio

4. controlla se nei log compaiono:

- `OPTIONS /api/attempt -> 204`
- `POST /api/attempt -> 204`

Interpretazione:

- se compaiono, il backend sta ricevendo e scrivendo
- se vedi solo `GET /`, la pagina si apre ma il browser non sta inviando il playtest
- se vedi errori `4xx` o `5xx`, c'e' un problema di rete, CORS o payload

## Problemi comuni

### 1. Il sito si apre ma il DB non si aggiorna

Controlla:

- `journalctl -u woordle-backend-test -f`
- `api-config.js` pubblicato su GitHub Pages o sul dominio frontend effettivo
- eventuali errori console nel browser
- risposta di `GET /api/daily` dal backend

Nota:

- se il backend e' dietro Caddy, i nuovi eventi dovrebbero mostrare l'IP reale del client e non piu' `127.0.0.1`, a patto che il proxy inoltri correttamente gli header standard (`X-Forwarded-For` / `X-Real-IP`)

### 2. Caddy risponde `502`

Significa in genere che:

- il backend Python e' giu'
- oppure Caddy e' partito prima che il backend fosse pronto

In quel caso:

```bash
sudo systemctl restart woordle-backend-test
sudo systemctl restart caddy
```

Poi verifica:

```bash
curl -I https://<backend-domain>
```

### 3. Dopo reboot non parte

Controlla:

```bash
systemctl is-enabled woordle-backend-test
systemctl is-enabled caddy
```

Risultato atteso:

- `enabled`

## Flusso operativo consigliato

Per uso quotidiano:

1. lascia backend e Caddy sempre gestiti da `systemd`
2. non avviare il backend a mano in una shell normale
3. usa `journalctl` per vedere cosa succede
4. usa `report_playtest.py` per rigenerare una vista leggibile dei dati

## Comandi piu' usati

```bash
systemctl status woordle-backend-test
systemctl status caddy
journalctl -u woordle-backend-test -f
journalctl -u caddy -f
sudo systemctl restart woordle-backend-test
sudo systemctl restart caddy
python3 report_playtest.py
```

## Note finali

- il backend e' pensato per girare in silenzio come servizio
- i log migliori sono quelli di `journalctl`
- la fonte dati principale e' sempre `data/playtest.db`
- il CSV e il report sono viste derivate, non la fonte primaria
