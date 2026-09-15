---
name: info
description: "Mostra lo stato attuale del cervello aziendale: cosa e' gia' configurato, cosa manca, se il grafo delle note e' collegato correttamente, e cosa fare dopo. Usa quando l'utente scrive /info o chiede lo stato/la situazione del cervello."
---

# /info

Fotografa lo stato del cervello aziendale. Comando di sola lettura: non scrive, non modifica e non rigenera nessun file (nemmeno `llms.txt` o `_showcase/showcase.md`, anche se non aggiornati).

## Cosa leggere

1. `llms.txt` (radice del vault): elenco di tutte le note per cartella, con summary.
2. `_showcase/showcase.md`: numeri del grafo (note totali, wikilink, componenti connesse). Se il file manca o sembra vecchio, dillo all'utente e suggerisci di rilanciare `python3 code/generate_showcase.py`, ma non farlo tu stesso in questo comando.
3. `workspace/canon-template.md`: per capire quali sezioni del setup sono compilate e quali no, con lo stesso criterio usato da `/setup`:
   - Identita': vuota se i campi dopo i due punti sono senza valore.
   - Prodotti/Reparti/Persone: vuote se contengono ancora la riga placeholder `{{...}}` senza righe reali aggiunte.
   - Clienti: vuota se la tabella ha solo la riga vuota.
   - KPI di fine periodo: vuota se i campi dopo i due punti sono senza valore.

## Cosa riportare all'utente

Rispondi in modo compatto (non un report lunghissimo), con queste parti:

1. **Cos'e' questo cervello**, in 1-2 righe: template di second brain aziendale con memoria statica (entita') e dinamica (diario).
2. **Stato del setup**: quali delle 6 sezioni del canon sono compilate e quali no (es. "Identita' e Prodotti fatti. Reparti, Persone, Clienti, KPI ancora da fare."). Se tutto e' vuoto, dillo chiaramente e suggerisci `/setup` come primo passo.
3. **Numeri del vault**: note totali e componenti connesse, presi da `_showcase/showcase.md`. Se le componenti connesse sono piu' di 1, avvisa esplicitamente: il grafo e' spezzato in isole, qualcosa non e' agganciato correttamente e va sistemato (tipicamente rilanciando `/setup` o aggiungendo a mano i wikilink mancanti sulle note isolate, che `python3 code/qa_gate.py` puo' aiutare a individuare).
4. **Prossimo passo consigliato**: se il canon non e' completo, suggerisci `/setup`. Se e' tutto configurato e il grafo e' a componente unica, suggerisci `/journal buongiorno` per iniziare la sessione di lavoro.

Non eseguire `qa_gate.py`, `generate_llms_txt.py` o `generate_showcase.py` da questo comando: sono passi di scrittura/rigenerazione che appartengono a `/setup`, non a `/info`.
