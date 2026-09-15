#!/usr/bin/env python3
"""Gate di qualita' per il cervello aziendale.

Setaccia ogni nota .md nelle cartelle di contenuto del vault, saltando
sources/ e workspace/ (materiale grezzo e scratch) e qualsiasi cartella
che inizia per "." o "_" (config, skill, output derivati), e la
controlla contro 6 regole:

1. Frontmatter completo: title, summary, tags, status, created, updated.
2. Massimo 300 righe di corpo per nota.
3. Almeno 3 wikilink [[...]] in uscita verso note che esistono davvero
   (bersagli unici, gli _index non valgono).
4. Zero link rotti: ogni [[bersaglio]] punta a una nota che esiste.
5. Zero orfani: ogni nota ha almeno 1 link in entrata (gli _index sono esentati).
6. Una sola componente connessa nel grafo delle note.

Uso:
    python3 qa_gate.py [percorso_vault]

Senza argomenti usa la cartella padre di questo script come radice del vault.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

EXCLUDED_FOLDERS = {"sources", "workspace"}


def is_excluded_folder(name: str) -> bool:
    return name in EXCLUDED_FOLDERS or name.startswith(".") or name.startswith("_")


REQUIRED_FRONTMATTER_KEYS = ["title", "summary", "tags", "status", "created", "updated"]
MAX_BODY_LINES = 300
MIN_OUTGOING_LINKS = 3
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)")


def is_index(stem: str) -> bool:
    return stem == "_index"


def parse_note(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    fm: dict[str, str] = {}
    body = text
    if lines and lines[0].strip() == "---":
        closing_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                closing_idx = i
                break
        if closing_idx is not None:
            for line in lines[1:closing_idx]:
                if not line.strip() or ":" not in line:
                    continue
                key, _, val = line.partition(":")
                fm[key.strip()] = val.strip()
            body = "\n".join(lines[closing_idx + 1 :])
    return fm, body, text


def extract_targets(raw_text: str) -> list[str]:
    return [m.strip() for m in WIKILINK_RE.findall(raw_text)]


def discover_notes(vault_root: Path):
    notes = {}  # stem -> path
    duplicates = []
    for folder in sorted(p.name for p in vault_root.iterdir() if p.is_dir()):
        if is_excluded_folder(folder):
            continue
        for path in sorted((vault_root / folder).rglob("*.md")):
            stem = path.stem
            if stem in notes:
                duplicates.append((stem, notes[stem], path))
            else:
                notes[stem] = path
    return notes, duplicates


def main():
    vault_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent

    notes, duplicates = discover_notes(vault_root)

    parsed = {}  # stem -> (fm, body, raw_text, path)
    for stem, path in notes.items():
        fm, body, raw_text = parse_note(path)
        parsed[stem] = (fm, body, raw_text, path)

    # Raccogli, per ogni nota, i link unici in uscita (esclusi self-link)
    outgoing = {}  # stem -> set(target stems as written, non necessariamente esistenti)
    for stem, (fm, body, raw_text, path) in parsed.items():
        targets = extract_targets(raw_text)
        outgoing[stem] = {t for t in targets if t != stem}

    errors = {n: [] for n in range(1, 7)}  # 1..6 -> list of strings

    # Regola 1: frontmatter completo
    for stem in sorted(parsed):
        fm, _, _, path = parsed[stem]
        missing = [k for k in REQUIRED_FRONTMATTER_KEYS if not fm.get(k, "").strip()]
        if missing:
            errors[1].append(f"{path.relative_to(vault_root)}: mancano {', '.join(missing)}")

    # Regola 2: max 300 righe di corpo
    for stem in sorted(parsed):
        _, body, _, path = parsed[stem]
        stripped = body.strip("\n")
        n_lines = stripped.count("\n") + 1 if stripped else 0
        if n_lines > MAX_BODY_LINES:
            errors[2].append(f"{path.relative_to(vault_root)}: {n_lines} righe di corpo (> {MAX_BODY_LINES})")

    # Regola 3: almeno 3 wikilink unici verso note reali (esclusi _index)
    for stem in sorted(parsed):
        _, _, _, path = parsed[stem]
        valid_unique = {t for t in outgoing[stem] if t in notes and not is_index(t)}
        if len(valid_unique) < MIN_OUTGOING_LINKS:
            found = ", ".join(sorted(valid_unique)) if valid_unique else "nessuno"
            errors[3].append(
                f"{path.relative_to(vault_root)}: {len(valid_unique)} link validi unici (< {MIN_OUTGOING_LINKS}) — trovati: {found}"
            )

    # Regola 4: zero link rotti
    for stem in sorted(parsed):
        _, _, _, path = parsed[stem]
        broken = sorted({t for t in outgoing[stem] if t not in notes})
        if broken:
            errors[4].append(f"{path.relative_to(vault_root)}: link rotti verso {', '.join(f'[[{b}]]' for b in broken)}")

    # Regola 5: zero orfani (almeno 1 link in entrata; _index esentati)
    incoming_count = {stem: 0 for stem in notes}
    for stem, targets in outgoing.items():
        for t in targets:
            if t in notes and t != stem:
                incoming_count[t] += 1
    for stem in sorted(parsed):
        if is_index(stem):
            continue
        _, _, _, path = parsed[stem]
        if incoming_count.get(stem, 0) == 0:
            errors[5].append(f"{path.relative_to(vault_root)}: 0 link in entrata")

    # Regola 6: una sola componente connessa (grafo non orientato)
    adjacency = {stem: set() for stem in notes}
    for stem, targets in outgoing.items():
        for t in targets:
            if t in notes and t != stem:
                adjacency[stem].add(t)
                adjacency[t].add(stem)

    visited = set()
    components = []
    for stem in notes:
        if stem in visited:
            continue
        component = set()
        stack = [stem]
        while stack:
            cur = stack.pop()
            if cur in component:
                continue
            component.add(cur)
            stack.extend(adjacency[cur] - component)
        visited |= component
        components.append(component)

    if len(components) > 1:
        components.sort(key=len, reverse=True)
        for i, comp in enumerate(components, start=1):
            members = ", ".join(sorted(parsed[s][3].relative_to(vault_root).as_posix() for s in comp))
            errors[6].append(f"Isola {i} ({len(comp)} note): {members}")

    # Report
    rule_titles = {
        1: "Regola 1 — Frontmatter completo",
        2: "Regola 2 — Massimo 300 righe di corpo",
        3: "Regola 3 — Almeno 3 wikilink unici verso note reali",
        4: "Regola 4 — Zero link rotti",
        5: "Regola 5 — Zero orfani (almeno 1 link in entrata)",
        6: "Regola 6 — Una sola componente connessa",
    }

    total_errors = sum(len(v) for v in errors.values())

    print(f"Vault: {vault_root}")
    print(f"Note controllate: {len(notes)} (escluse sources/ e workspace/)")
    if duplicates:
        print("\nATTENZIONE — stem duplicati (nomi file uguali in cartelle diverse):")
        for stem, p1, p2 in duplicates:
            print(f"  - {stem}: {p1.relative_to(vault_root)} vs {p2.relative_to(vault_root)}")
    print()

    if total_errors == 0:
        print("OK, 0 errori")
        return 0

    for n in range(1, 7):
        print(f"## {rule_titles[n]}")
        if not errors[n]:
            print("Nessun errore.")
        else:
            for e in errors[n]:
                print(f"- {e}")
        print()

    print(f"Totale errori: {total_errors}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
