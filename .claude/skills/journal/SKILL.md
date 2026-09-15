---
name: journal
description: "Gestisce il diario di lavoro del cervello aziendale (memoria dinamica): briefing a inizio sessione, nota di chiusura sessione, riassunto di fine giornata. Usa quando l'utente scrive /journal, 'buongiorno', 'chiudi sessione' o 'fine giornata' nel contesto del cervello aziendale."
---

# /journal

Tiene viva la memoria dinamica del cervello (il diario di lavoro) e la aggancia sempre alla memoria statica (le note reali di entita', KPI, progetti) coi wikilink. Non esiste mai una nota di diario sciolta nel vuoto.

Tre comandi, invocati come argomento: `/journal buongiorno`, `/journal chiudi sessione`, `/journal fine giornata`.

## Percorsi

- Indice del cervello: `llms.txt` (radice del vault)
- Note sessione: `workspace/journal/sessions/sessione-<YYYY-MM-DD>.md` (se piu' sessioni nello stesso giorno, aggiungi suffisso: `sessione-<YYYY-MM-DD>-2.md`, `-3.md`, ecc.)
- Note giornata: `workspace/journal/daily/<YYYY-MM-DD>.md`
- Template: `workspace/journal/_templates/template-sessione.md` e `workspace/journal/_templates/template-daily.md`

`workspace/` e' escluso da `qa_gate.py` e da `generate_llms_txt.py`: le note di diario non devono rispettare i vincoli delle note vere (min. 3 link, zero orfani) e non compaiono in `llms.txt`. Non serve rigenerare `llms.txt` o lo showcase dopo aver scritto nel journal.

## Regole valide per tutti e tre i comandi

- Le date sono sempre in formato `YYYY-MM-DD`, mai relative ("oggi", "ieri"). Ricava la data reale con il comando di sistema (`date +%F`), non a memoria.
- Ogni nota di diario deve avere almeno un `[[wikilink]]` verso una nota di memoria statica realmente esistente (cliente, persona, prodotto, KPI, progetto...). Se non e' chiaro a quale entita' agganciare la nota, chiedilo all'utente invece di indovinare o lasciare la nota scollegata.
- Non inventare entita': i wikilink nel `related` e nel corpo devono puntare solo a note che esistono gia' nel cervello (verificale in `llms.txt` o con un giro nelle cartelle di contenuto).
- Scrivi in italiano naturale. Non usare la lineetta lunga (m-dash "—"); usa virgole, punti o parentesi.
- Prima di scrivere qualsiasi file (comandi 2 e 3), esponi sempre il riassunto richiesto e aspetta l'ok esplicito dell'utente. Non scrivere di iniziativa.

---

## 1. `buongiorno` — inizio sessione (solo briefing, non scrive nulla)

1. Leggi `llms.txt` per avere il quadro delle entita' vive del cervello.
2. Trova l'ultima nota per data in `workspace/journal/sessions/` (se ce ne sono piu' con la stessa data, considera anche quelle). Se la cartella e' vuota, e' la prima sessione: dillo esplicitamente.
3. Dai un briefing in 5 righe, non di piu':
   - dove eravamo rimasti (riassunto dell'ultima sessione/e)
   - cosa era rimasto aperto (dalla sezione "Aperto" dell'ultima nota)
   - cosa conviene affrontare oggi, in ordine di priorita'
4. Non creare, modificare o toccare nessun file. Solo output a schermo.

## 2. `chiudi sessione` — fine sessione (scrive la nota di sessione)

1. Ricostruisci dal contesto della conversazione cosa e' stato fatto in questa sessione di lavoro.
2. Esponi all'utente in 3 righe cosa hai capito che e' stato fatto. Fermati e aspetta l'ok.
3. Solo dopo l'ok:
   - Calcola la data odierna (`YYYY-MM-DD`).
   - Determina il nome file: `sessione-<data>.md`, o `sessione-<data>-2.md` ecc. se esiste gia' una sessione per oggi.
   - Copia la struttura da `workspace/journal/_templates/template-sessione.md`.
   - Frontmatter:
     - `title`: "Sessione <data>"
     - `summary`: una sola frase su cosa e' stato fatto
     - `tags`: `[workspace, type/session]`
     - `status`: `done`
     - `created` e `updated`: la data odierna
     - `related`: wikilink, su una riga, a tutte le entita' statiche toccate oggi (clienti, KPI, progetti, persone...)
   - Corpo in tre sezioni, brevi:
     - `## Fatto`: cosa si e' concluso
     - `## Deciso`: le scelte prese e il perche'
     - `## Aperto`: cosa resta in sospeso
   - Verifica che ci sia almeno un wikilink verso un'entita' reale (in `related` o nel corpo). Se non ce n'e' nessuna evidente, chiedi all'utente a quale entita' agganciare la nota prima di scrivere.
   - Scrivi il file in `workspace/journal/sessions/`.

## 3. `fine giornata` — riassunto di giornata (scrive il daily)

1. Leggi tutte le note `sessione-<data odierna>*.md` in `workspace/journal/sessions/` (gestisci il caso di piu' sessioni con suffisso numerico).
2. Esponi all'utente in 3 righe cosa e' successo oggi in totale, fondendo le sessioni. Fermati e aspetta l'ok.
3. Solo dopo l'ok:
   - File: `workspace/journal/daily/<data odierna>.md`.
   - Copia la struttura da `workspace/journal/_templates/template-daily.md`.
   - Frontmatter:
     - `title`: "Giornata <data>"
     - `summary`: una sola frase sintetica sulla giornata
     - `tags`: `[workspace, type/daily]`
     - `status`: `done`
     - `created` e `updated`: la data odierna
     - `related`: wikilink a tutte le sessioni della giornata + le entita' principali toccate
   - Corpo: sintesi unica in tre sezioni (`## Fatto`, `## Deciso`, `## Aperto`), fondendo le sessioni senza ripeterle riga per riga.
   - In fondo, sezione `## Sessioni` con l'elenco puntato dei wikilink a ogni nota di sessione del giorno.
   - Scrivi il file in `workspace/journal/daily/`.

Se in un giorno non esiste nessuna nota di sessione, dillo all'utente invece di inventare un daily vuoto.
