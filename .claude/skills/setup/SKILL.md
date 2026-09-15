---
name: setup
description: "Intervista guidata per configurare da zero il cervello aziendale con i dati reali di un'azienda. Usa quando l'utente scrive /setup, chiede di 'impostare' o 'configurare' il cervello, o di iniziare a popolare il template con la propria azienda."
---

# /setup

Guida un'intervista a sezioni per raccogliere i fatti reali di un'azienda, li registra in `workspace/canon-template.md`, poi li scompone in note finali vere agganciate al resto del cervello. E' ripetibile: se rilanciata, riprende solo dalle sezioni ancora vuote.

## Regole generali

- Date sempre in formato `YYYY-MM-DD`, mai relative. Usa `date +%F` per la data odierna quando serve.
- Nessuna entita' inventata: ogni wikilink scritto deve puntare a una nota che esiste davvero o che stai creando tu stesso in questa sessione di setup.
- Frontmatter completo su ogni nota nuova: `title`, `summary` (una frase), `tags`, `status: active`, `created`, `updated`, `related` (lista di wikilink).
- Italiano naturale, niente lineetta lunga ("—"). Usa virgole o parentesi.
- Non scrivere mai le note finali senza un riassunto preventivo e l'ok esplicito dell'utente.

## Passo 1 — leggi lo stato del canon

Apri `workspace/canon-template.md`. Per ciascuna delle 6 sezioni, determina se e' gia' compilata o ancora vuota:

- **Identita'**: vuota se i campi (Missione, ICP, Offerta, Posizionamento, Sedi, Anno di fondazione, Numero di dipendenti) sono senza valore dopo i due punti.
- **Prodotti**: vuota se contiene ancora la riga placeholder `{{nome prodotto}} — {{cosa fa}}` e nessuna riga reale.
- **Reparti**: vuota se contiene ancora `{{nome reparto}} — {{funzione continua}}` senza righe reali.
- **Persone e ruoli**: vuota se contiene ancora `{{nome}} — {{ruolo}}` senza righe reali.
- **Clienti**: vuota se la tabella ha solo la riga vuota `| | | | |` senza clienti reali.
- **KPI di fine periodo**: vuota se i campi (ARR totale, Clienti attivi, Churn, NRR, Edifici gestiti) sono senza valore.

Se tutte le sezioni sono gia' compilate e le note finali corrispondenti esistono gia', dillo all'utente e chiedi se vuole rivedere/aggiornare qualcosa invece di ripartire da zero.

## Passo 2 — intervista a sezioni

Procedi nell'ordine: Identita' → Prodotti → Reparti → Persone → Clienti → KPI di fine periodo. Salta le sezioni gia' compilate (a meno che l'utente non chieda esplicitamente di rivederle).

Per ogni sezione ancora vuota:
1. Fai le domande necessarie a raccogliere i dati di quella sezione (una sezione alla volta, non tutte insieme). Usa `AskUserQuestion` per scelte chiuse o campi brevi, testo libero per descrizioni.
2. Scrivi le risposte in `workspace/canon-template.md`, sostituendo i placeholder di quella sezione con i dati reali.
3. Per la sezione Clienti e KPI, dopo averle compilate entrambe controlla i check di coerenza gia' presenti in fondo al canon: somma ARR dei clienti = ARR totale, somma immobili dei clienti = edifici gestiti. Se non tornano, segnalalo e chiedi come correggere prima di proseguire.
4. Passa alla sezione successiva.

Se l'utente vuole fermarsi a meta' e riprendere un'altra volta, va bene: il canon resta parzialmente compilato e la prossima invocazione di `/setup` riparte da dove si era interrotto (passo 1).

## Passo 3 — conferma prima di scrivere le note finali

Una volta che tutte le sezioni necessarie sono compilate (l'utente puo' anche scegliere di generare le note con solo alcune sezioni fatte, se lo chiede esplicitamente), riassumi in poche righe cosa hai raccolto: identita', quanti prodotti/reparti/persone/clienti, i KPI. Chiedi conferma esplicita prima di scrivere qualsiasi nota. Non procedere senza ok.

## Passo 4 — scomposizione in note finali

Dopo l'ok, per ogni elemento del canon crea la nota corrispondente usando il template giusto in `docs/templates/`:

- Identita' → `self/self-identita-<nome-azienda>.md` da `template-self-identita.md`
- Ogni prodotto → `entities/prodotto-<nome>.md` da `template-prodotto.md`
- Ogni reparto → `areas/area-<nome>.md` da `template-reparto.md`
- Ogni persona → `entities/persona-<nome>.md` da `template-persona.md`
- Ogni cliente → `entities/cliente-<nome>.md` da `template-cliente.md`
- KPI del periodo → `data/kpi-<periodo>.md` da `template-kpi-periodo.md`

Regole di collegamento mentre scrivi (la nota di identita' fa da hub e tiene tutto in un'unica componente connessa):
- La nota di identita' linka tutti i prodotti, tutti i reparti e la persona di riferimento commerciale se c'e'.
- Ogni prodotto linka l'identita' e, se noto, il reparto responsabile.
- Ogni reparto linka l'identita' e le persone che ne fanno parte.
- Ogni persona linka il reparto e/o i prodotti di cui si occupa.
- Ogni cliente linka i prodotti che usa, la persona commerciale di riferimento, e la nota KPI del periodo.
- La nota KPI linka l'identita' e tutti i clienti conteggiati.

Ogni nota deve avere almeno 3 wikilink unici verso note reali (regola del gate di qualita', vedi passo 5). Se una nota rischia di averne meno di 3, aggiungi un collegamento sensato invece di lasciarla sotto soglia.

## Passo 5 — gate di connessione obbligatorio

Esegui `python3 code/qa_gate.py` dalla radice del vault. Il setup non si considera concluso finche' l'esito non e' pulito (0 errori) sulle note appena create. In particolare verifica:

- **Regola 1** (frontmatter completo) su ogni nota nuova.
- **Regola 3** (almeno 3 wikilink unici verso note reali): se una nota nuova ne ha meno, aggiungi collegamenti pertinenti (non forzati/inventati) e ricontrolla.
- **Regola 4** (zero link rotti): ogni `[[wikilink]]` scritto deve puntare a una nota che esiste davvero.
- **Regola 5** (zero orfani): ogni nota nuova deve avere almeno un link in entrata da un'altra nota (es. se il prodotto linka l'identita', assicurati che anche l'identita' linki il prodotto, cosi' nessuno dei due resta orfano).
- **Regola 6** (una sola componente connessa nell'intero vault): tutte le note nuove devono risultare in un unico grafo, tipicamente perche' passano tutte dalla nota di identita'. Se `qa_gate.py` segnala piu' isole, non ignorarlo: trova la nota scollegata e aggiungile il link mancante verso l'identita' o un'altra nota pertinente, poi rilancia il gate.

Se il gate segnala errori, correggi le note appena scritte e rilancia `python3 code/qa_gate.py` finche' non riporta "OK, 0 errori". Solo allora prosegui al passo successivo.

## Passo 6 — rigenerazione dei derivati

Esegui `python3 code/generate_llms_txt.py` e `python3 code/generate_showcase.py`. Mostra all'utente i numeri finali di `_showcase/showcase.md` (note totali, componenti connesse) come conferma che tutto e' scritto e agganciato correttamente.

## Chiusura

Ricorda all'utente che puo' usare `/info` in qualsiasi momento per vedere lo stato del cervello, e `/journal buongiorno` per iniziare la prima sessione di lavoro vera e propria.
