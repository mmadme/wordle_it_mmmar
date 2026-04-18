# Activity DB - Executive Summary

- Periodo: `2026-04-04 00:00:00 UTC` -> `2026-04-17 23:59:59 UTC`
- Fonte: `data/playtest.db`, tabella `playtest_events`
- Vista usata: traffico pubblico, con esclusione di `localhost` e richieste `curl` di smoke test

## Snapshot

| KPI | Valore |
| --- | ---: |
| Giocatori unici | 32 |
| Sessioni giocate | 124 |
| Sessioni daily | 66 |
| Sessioni non-daily | 58 |
| Sessioni concluse | 113 |
| Sessioni vinte | 100 |
| Sessioni medie/giorno | 8.86 |
| Utenti medi/giorno | 4.57 |
| Eventi medi/giorno | 52.29 |

## Lettura veloce

- Il traffico e' ancora concentrato su pochi utenti forti: i primi 6 client generano `69` sessioni su `124`, cioe' il `55.6%` del totale.
- La ricorrenza e' discreta ma non ancora robusta: `17/32` utenti (`53.1%`) fanno almeno 2 sessioni, mentre `12/32` (`37.5%`) tornano in almeno 2 giorni distinti.
- Il fondo del funnel e' ancora largo: `15/32` utenti (`46.9%`) fanno una sola sessione e `20/32` (`62.5%`) risultano attivi in un solo giorno.
- La daily oggi regge leggermente meglio della infinita sul fronte qualita' dell'esperienza: stesso completion rate di fatto, ma meno tentativi medi e win rate piu' alto.

## Top Player

| Client ID | Sessioni | Giorni attivi | Daily | Non-daily | Vinte |
| --- | ---: | ---: | ---: | ---: | ---: |
| `68d0fc18-8e0b-4e4c-aa01-3c69f0e7b9ae` | 16 | 9 | 8 | 8 | 15 |
| `6527f631-cb24-42a1-a018-eb1941612f22` | 13 | 2 | 2 | 11 | 10 |
| `884475ac-4460-4afc-aa1a-44f80e62833b` | 11 | 4 | 5 | 6 | 8 |
| `f0d9957e-a049-47a1-8ed0-565f62ba1e2f` | 11 | 7 | 8 | 3 | 11 |
| `27056573-06dc-4b7b-97e7-fefe1c2bd298` | 9 | 1 | 1 | 8 | 7 |
| `cc699fe8-86eb-4e47-bc34-b12e66a11610` | 9 | 3 | 5 | 4 | 7 |

## Ricorrenza

### Sessioni per utente

| Sessioni nel periodo | Utenti |
| --- | ---: |
| 1 | 15 |
| 2 | 5 |
| 3 | 1 |
| 4 | 1 |
| 5 | 1 |
| 6 | 3 |
| 9 | 2 |
| 11 | 2 |
| 13 | 1 |
| 16 | 1 |

### Giorni attivi per utente

| Giorni attivi | Utenti |
| --- | ---: |
| 1 | 20 |
| 2 | 5 |
| 3 | 2 |
| 4 | 3 |
| 7 | 1 |
| 9 | 1 |

## Daily vs Infinita

| Metrica | Daily | Non-daily |
| --- | ---: | ---: |
| Sessioni | 66 | 58 |
| Sessioni concluse | 60 | 53 |
| Sessioni vinte | 55 | 45 |
| Completion rate | 90.9% | 91.4% |
| Win rate su sessioni | 83.3% | 77.6% |
| Tentativi medi per sessione | 3.65 | 4.48 |
| Tentativi medi su sessioni concluse | 3.82 | 4.60 |

Lettura:
- La daily e' piu' efficiente: si chiude con meno tentativi medi e con win rate piu' alto.
- L'infinita resta utile per volume, ma sembra piu' dispersiva: richiede piu' guess e produce piu' parole "rituali" ripetute.

## Picchi Giornalieri

| Giorno | Sessioni | Utenti unici | Eventi |
| --- | ---: | ---: | ---: |
| 2026-04-16 | 18 | 10 | 116 |
| 2026-04-11 | 16 | 6 | 106 |
| 2026-04-12 | 14 | 7 | 85 |
| 2026-04-15 | 14 | 7 | 93 |
| 2026-04-14 | 12 | 6 | 81 |

Lettura:
- Il picco massimo e' `2026-04-16`, sia per sessioni sia per utenti unici.
- `2026-04-11` ha meno utenti del 16 aprile ma piu' intensita' per utente, quindi probabilmente piu' restart o piu' partite per singolo giocatore.

## Vocaboli Dominanti

### Top vocaboli in daily

| Parola | Conteggio |
| --- | ---: |
| `sedia` | 14 |
| `ruota` | 9 |
| `treno` | 8 |
| `perde` | 7 |
| `lorde` | 6 |
| `reame` | 6 |
| `resta` | 6 |

### Top vocaboli in infinita / non-daily

| Parola | Conteggio |
| --- | ---: |
| `troia` | 28 |
| `buche` | 23 |
| `figli` | 23 |
| `mondo` | 13 |
| `sedia` | 5 |
| `ruota` | 4 |
| `cirio` | 3 |

### Guess rifiutati piu' visibili

| Parola | Rifiuti | Modalita' prevalente |
| --- | ---: | --- |
| `cirio` | 3 | non-daily |
| `ireca` | 3 | non-daily |
| `negro` | 2 | non-daily |
| `fursa` | 2 | daily |
| `giolo` | 2 | non-daily |

Lettura:
- In infinita si vede chiaramente un comportamento da "parole opener" ripetute (`troia`, `buche`, `figli`, `mondo`).
- In daily il lessico e' piu' distribuito e piu' coerente con il puzzle del giorno.
- I rifiuti non sono altissimi in volume assoluto, ma indicano alcune parole che gli utenti si aspettano siano valide.

## Indicazioni Operative

- Se vuoi massimizzare retention, ha senso spingere la daily come prodotto principale: e' piu' compatta, piu' vincibile e meno dispersiva.
- L'infinita sembra ottima per power user e replay, ma andrebbe monitorata con KPI dedicati per non confondere i segnali di engagement con sessioni ripetitive.
- Vale la pena osservare da vicino le parole-opener ricorrenti: possono diventare un segnale utile per ranking difficolta', tutorial o suggerimenti futuri.
- Le parole rifiutate ricorrenti sono candidate per una review del dizionario, o almeno per una lista di controllo redazionale.

## File di supporto

- Report completo: `docs/db_activity_last_2_weeks_2026-04-17.md`
- Utenti attivi: `data/db_activity_users_last_2_weeks_2026-04-17.csv`
- Sessioni: `data/db_activity_sessions_last_2_weeks_2026-04-17.csv`
- Vocaboli: `data/db_activity_word_counts_last_2_weeks_2026-04-17.csv`
