# Activity DB Report - Last 2 Weeks

- Periodo analizzato: `2026-04-04 00:00:00 UTC -> 2026-04-17 23:59:59 UTC`
- Fonte: `data/playtest.db`, tabella `playtest_events`
- Vista principale del report: traffico pubblico, con esclusione di localhost / `curl` di smoke test

## KPI principali (traffico pubblico)

| KPI | Valore |
| --- | ---: |
| Eventi | 732 |
| Sessioni giocate | 124 |
| Sessioni concluse | 113 |
| Sessioni vinte | 100 |
| Sessioni daily | 66 |
| Sessioni non-daily | 58 |
| Giocatori unici | 32 |
| Giocatori ricorrenti (>=2 giorni) | 12 |
| Giocatori ricorrenti (>=2 sessioni) | 17 |
| Flusso medio giornaliero: sessioni/giorno | 8.86 |
| Flusso medio giornaliero: utenti/giorno | 4.57 |
| Flusso medio giornaliero: eventi/giorno | 52.29 |
| Vocaboli distinti provati | 386 |

## Impatto del traffico di test escluso

| Vista | Eventi | Sessioni | Giocatori unici |
| --- | ---: | ---: | ---: |
| Raw DB | 810 | 142 | 35 |
| Pubblico (escluso localhost/curl) | 732 | 124 | 32 |
| Delta escluso | 78 | 18 | 3 |

## Flusso giornaliero (traffico pubblico)

| Giorno | Eventi | Sessioni | Utenti unici |
| --- | ---: | ---: | ---: |
| 2026-04-05 | 49 | 10 | 5 |
| 2026-04-06 | 20 | 5 | 2 |
| 2026-04-07 | 34 | 6 | 3 |
| 2026-04-08 | 17 | 3 | 1 |
| 2026-04-09 | 54 | 11 | 7 |
| 2026-04-10 | 33 | 7 | 3 |
| 2026-04-11 | 106 | 16 | 6 |
| 2026-04-12 | 85 | 14 | 7 |
| 2026-04-13 | 40 | 7 | 6 |
| 2026-04-14 | 81 | 12 | 6 |
| 2026-04-15 | 93 | 14 | 7 |
| 2026-04-16 | 116 | 18 | 10 |
| 2026-04-17 | 4 | 1 | 1 |

## Utenti attivi (traffico pubblico)

| Client ID | Giorni attivi | Sessioni | Daily | Non-daily | Concluse | Vinte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `68d0fc18-8e0b-4e4c-aa01-3c69f0e7b9ae` | 9 | 16 | 8 | 8 | 16 | 15 |
| `6527f631-cb24-42a1-a018-eb1941612f22` | 2 | 13 | 2 | 11 | 13 | 10 |
| `884475ac-4460-4afc-aa1a-44f80e62833b` | 4 | 11 | 5 | 6 | 10 | 8 |
| `f0d9957e-a049-47a1-8ed0-565f62ba1e2f` | 7 | 11 | 8 | 3 | 11 | 11 |
| `27056573-06dc-4b7b-97e7-fefe1c2bd298` | 1 | 9 | 1 | 8 | 9 | 7 |
| `cc699fe8-86eb-4e47-bc34-b12e66a11610` | 3 | 9 | 5 | 4 | 9 | 7 |
| `8acaf90d-f781-485f-be08-b0276e153290` | 4 | 6 | 4 | 2 | 5 | 5 |
| `9429ff15-e433-480e-977b-91a64647da7f` | 4 | 6 | 4 | 2 | 5 | 5 |
| `id-1775409608874-4jyh6jbu` | 1 | 6 | 1 | 5 | 6 | 6 |
| `30436058-3856-4e22-baf1-dde66220f99b` | 1 | 5 | 1 | 4 | 5 | 4 |
| `67f1e14a-ffd1-42c5-be91-a66b43c92979` | 3 | 4 | 4 | 0 | 4 | 4 |
| `6356f962-6fe9-4bc5-bf46-f7484a49edf0` | 2 | 3 | 2 | 1 | 2 | 2 |
| `0fe6c40c-426f-4340-88a2-b5890f3887a0` | 1 | 2 | 1 | 1 | 2 | 2 |
| `53dc979e-1370-47b6-97d7-76e88b6beee3` | 1 | 2 | 1 | 1 | 2 | 1 |
| `6028d993-5cc3-4a4b-a68f-35ae89848c57` | 2 | 2 | 2 | 0 | 2 | 2 |
| `eb0c0bc0-cc69-4b73-bbf8-9738d6152ee4` | 2 | 2 | 2 | 0 | 1 | 1 |
| `ff07af4e-7024-46dd-a2ff-9a380016716d` | 2 | 2 | 1 | 1 | 1 | 1 |
| `0bfa1148-8bed-4ed0-99af-0e154c055f93` | 1 | 1 | 1 | 0 | 1 | 1 |
| `707e2421-3206-4eea-bdf5-4740d13f4bb1` | 1 | 1 | 1 | 0 | 1 | 1 |
| `738160d7-4c7d-4684-a437-19c02ae0b0b7` | 1 | 1 | 1 | 0 | 1 | 1 |
| `7a91ecc5-448d-47e0-99fb-4a60acd86c67` | 1 | 1 | 1 | 0 | 1 | 1 |
| `8b65d837-05af-4d4f-8e73-0e72f6b68b13` | 1 | 1 | 1 | 0 | 1 | 1 |
| `98097e9c-644d-44f6-a026-50cdd797a735` | 1 | 1 | 1 | 0 | 0 | 0 |
| `9f3a78d7-c30f-4c27-bfc6-ca4e2b88978b` | 1 | 1 | 1 | 0 | 0 | 0 |
| `b8a0deb2-b841-4d75-b414-d21366212a6e` | 1 | 1 | 1 | 0 | 1 | 0 |
| `c30a6a90-e8f6-4752-8715-b647175bf555` | 1 | 1 | 0 | 1 | 0 | 0 |
| `ca5cdd82-a51d-4201-a1a8-11315d6e1c2f` | 1 | 1 | 1 | 0 | 1 | 1 |
| `f901c1b2-6da9-407a-b4ce-c52cc07662fb` | 1 | 1 | 1 | 0 | 1 | 1 |
| `id-1775408596208-p8cw914f` | 1 | 1 | 1 | 0 | 1 | 1 |
| `id-1775409741756-cqamkyoh` | 1 | 1 | 1 | 0 | 1 | 1 |
| `id-1775411858955-kmpfx039` | 1 | 1 | 1 | 0 | 0 | 0 |
| `id-1775424565174-tqk570ug` | 1 | 1 | 1 | 0 | 0 | 0 |

Dettaglio parole per utente e sessioni complete nei CSV allegati:
- `data/db_activity_users_last_2_weeks_2026-04-17.csv`
- `data/db_activity_sessions_last_2_weeks_2026-04-17.csv`
- `data/db_activity_word_counts_last_2_weeks_2026-04-17.csv`

## Top vocaboli provati (traffico pubblico)

| Vocabolo | Totale | Accettati | Rifiutati | Daily | Non-daily |
| --- | ---: | ---: | ---: | ---: | ---: |
| `troia` | 33 | 33 | 0 | 5 | 28 |
| `buche` | 28 | 28 | 0 | 5 | 23 |
| `figli` | 26 | 26 | 0 | 3 | 23 |
| `sedia` | 19 | 19 | 0 | 14 | 5 |
| `mondo` | 14 | 14 | 0 | 1 | 13 |
| `ruota` | 13 | 13 | 0 | 9 | 4 |
| `resta` | 9 | 9 | 0 | 6 | 3 |
| `treno` | 8 | 8 | 0 | 8 | 0 |
| `perde` | 7 | 7 | 0 | 7 | 0 |
| `lorde` | 6 | 6 | 0 | 6 | 0 |
| `reame` | 6 | 6 | 0 | 6 | 0 |
| `blusa` | 5 | 5 | 0 | 5 | 0 |
| `scudo` | 5 | 5 | 0 | 5 | 0 |
| `museo` | 4 | 4 | 0 | 3 | 1 |
| `scova` | 4 | 4 | 0 | 4 | 0 |
| `tosse` | 4 | 4 | 0 | 4 | 0 |
| `aiuto` | 3 | 3 | 0 | 2 | 1 |
| `cirio` | 3 | 0 | 3 | 0 | 3 |
| `consa` | 3 | 3 | 0 | 3 | 0 |
| `felce` | 3 | 3 | 0 | 1 | 2 |
| `furia` | 3 | 3 | 0 | 3 | 0 |
| `ireca` | 3 | 0 | 3 | 0 | 3 |
| `iride` | 3 | 3 | 0 | 3 | 0 |
| `pulsa` | 3 | 3 | 0 | 3 | 0 |
| `ruote` | 3 | 3 | 0 | 2 | 1 |
| `tuono` | 3 | 3 | 0 | 0 | 3 |
| `umida` | 3 | 3 | 0 | 3 | 0 |
| `audio` | 2 | 2 | 0 | 2 | 0 |
| `carte` | 2 | 2 | 0 | 1 | 1 |
| `chilo` | 2 | 2 | 0 | 1 | 1 |
| `clima` | 2 | 2 | 0 | 0 | 2 |
| `dormo` | 2 | 2 | 0 | 1 | 1 |
| `ebrei` | 2 | 2 | 0 | 1 | 1 |
| `festa` | 2 | 2 | 0 | 1 | 1 |
| `forme` | 2 | 2 | 0 | 2 | 0 |
| `fresa` | 2 | 2 | 0 | 2 | 0 |
| `fursa` | 2 | 0 | 2 | 2 | 0 |
| `giolo` | 2 | 0 | 2 | 0 | 2 |
| `grida` | 2 | 2 | 0 | 0 | 2 |
| `ladro` | 2 | 2 | 0 | 0 | 2 |

Il CSV dei vocaboli contiene l'elenco completo ordinato per frequenza.
