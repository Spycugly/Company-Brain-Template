# Template Company Brain

Un cervello aziendale che vive in un vault Obsidian: le note sono collegate a wikilink e formano un grafo, non un archivio di file sciolti. Questo repository e' un **template vuoto e condivisibile**: struttura di cartelle, template delle note, script di qualita' e skill guidate gia' pronti, cartelle di contenuto vuote in attesa della tua azienda reale.

`llms.txt`, alla radice, e' l'indice pensato per le AI (elenco di tutte le note per cartella). Questo file e' la guida pensata per le persone.

## Due strati di memoria

- **Memoria statica**: le note delle entita' vere (identita' aziendale, prodotti, reparti, persone, clienti, KPI, progetti). Vivono nelle cartelle `self/`, `areas/`, `projects/`, `concepts/`, `docs/`, `entities/`, `data/`, `code/`, `outputs/`. Cambiano di rado.
- **Memoria dinamica**: il diario di lavoro, in `workspace/journal/` (sessioni e riassunti di giornata). Cambia ogni giorno e resta sempre agganciato alla memoria statica coi wikilink.

Due cartelle non fanno parte del grafo delle note vere e proprie:
- `sources/`: materiale grezzo non ancora processato (trascrizioni, appunti, documenti).
- `workspace/`: file di lavoro e scratch, incluso `canon-template.md` (il foglio dove si raccolgono i fatti prima di diventare note finali) e il diario.

## Cosa c'e' gia' dentro

- `docs/templates/`: un template per ogni tipo di nota (identita', prodotto, reparto, persona, cliente, KPI di periodo), gia' collegati tra loro a wikilink. `/setup` li usa per generare le tue note reali.
- `code/`: tre script di infrastruttura, generici e non legati a nessuna azienda specifica: `qa_gate.py` (verifica qualita' e collegamenti), `generate_llms_txt.py` e `generate_showcase.py` (rigenerano gli indici derivati).
- `self/`, `areas/`, `projects/`, `concepts/`, `entities/`, `data/`, `outputs/`: vuote, pronte per le tue note reali.

## Percorso di setup

1. Leggi questa guida (fatto).
2. Lancia `/setup`. Ti fara' domande a sezioni (identita', prodotti, reparti, persone, clienti, KPI di fine periodo), riempiendo via via `workspace/canon-template.md`.
3. Al termine dell'intervista, `/setup` scompone il canon in note finali vere (usando i template di `docs/templates/`), le collega alle entita' giuste e lancia `code/qa_gate.py` per verificare che tutto sia scritto bene e collegato correttamente. Puoi rilanciare `/setup` in qualsiasi momento per completare le sezioni ancora mancanti.
4. Da quel momento, usa `/journal` per il lavoro quotidiano:
   - `/journal buongiorno` a inizio sessione, per un briefing su dove eri rimasto.
   - `/journal chiudi sessione` a fine sessione, per lasciare una nota di diario.
   - `/journal fine giornata` a fine giornata, per un riassunto che fonde le sessioni del giorno.
5. Usa `/info` in qualsiasi momento per vedere lo stato del cervello: cosa e' gia' configurato, cosa manca, se il grafo delle note e' tutto collegato.

## Qualita' e coerenza

Ogni nota (fuori da `sources/` e `workspace/`) deve avere frontmatter completo, almeno 3 wikilink verso note reali, nessun link rotto, nessuna nota orfana, e l'intero vault deve restare un unico grafo connesso. Questo viene verificato da `python3 code/qa_gate.py`. Due script rigenerano i file derivati dopo ogni modifica strutturale: `python3 code/generate_llms_txt.py` e `python3 code/generate_showcase.py` (mai modificare `llms.txt` o `_showcase/showcase.md` a mano, sono sempre rigenerati).
