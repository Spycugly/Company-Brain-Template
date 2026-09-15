#!/usr/bin/env python3
"""Genera la fotografia dello showcase del cervello aziendale.

_showcase/showcase.md e' DERIVATO: questo script lo rigenera da capo ogni
volta. Non va mai modificato a mano.

Conta le note nelle 11 cartelle del vault (sources/ e workspace/ escluse), i
wikilink validi che le collegano, il numero di componenti connesse del grafo,
una tabella "note per cartella" e l'elenco degli hub (il summary dell'_index
di ogni cartella, quando esiste).

Uso:
    python3 generate_showcase.py [percorso_vault]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

EXCLUDED_FOLDERS = {"sources", "workspace"}
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)")


def is_excluded_folder(name: str) -> bool:
    return name in EXCLUDED_FOLDERS or name.startswith(".") or name.startswith("_")


def parse_note(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    fm: dict[str, str] = {}
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
    return fm, text


def discover_notes(vault_root: Path):
    by_folder: dict[str, list[Path]] = {}
    for folder in sorted(p.name for p in vault_root.iterdir() if p.is_dir()):
        if is_excluded_folder(folder):
            continue
        paths = sorted((vault_root / folder).rglob("*.md"))
        by_folder[folder] = paths
    return by_folder


def main():
    vault_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent

    by_folder = discover_notes(vault_root)
    all_paths = [p for paths in by_folder.values() for p in paths]
    notes = {p.stem: p for p in all_paths}  # stem -> path (per risoluzione link)

    parsed = {stem: parse_note(path) for stem, path in notes.items()}

    outgoing = {}
    for stem, (fm, raw_text) in parsed.items():
        targets = {m.strip() for m in WIKILINK_RE.findall(raw_text)}
        outgoing[stem] = {t for t in targets if t != stem and t in notes}

    total_notes = len(notes)
    raw_valid_links = sum(len(t) for t in outgoing.values())

    adjacency = {stem: set() for stem in notes}
    edges = set()
    for stem, targets in outgoing.items():
        for t in targets:
            adjacency[stem].add(t)
            adjacency[t].add(stem)
            edges.add(frozenset((stem, t)))

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

    n_components = len(components)

    lines = []
    lines.append("# Showcase — Cervello Aziendale")
    lines.append("")
    lines.append(
        "> Fotografia DERIVATA, generata da `code/generate_showcase.py`. "
        "Non modificarla a mano: rigenerala da capo eseguendo lo script."
    )
    lines.append("")
    lines.append("## Numeri")
    lines.append("")
    lines.append(f"- Note totali: {total_notes}")
    lines.append(f"- Wikilink totali (occorrenze valide verso note esistenti): {raw_valid_links}")
    lines.append(f"- Collegamenti unici (archi del grafo): {len(edges)}")
    lines.append(f"- Componenti connesse: {n_components} {'(tutto collegato)' if n_components == 1 else '(grafo spezzato in isole)'}")
    lines.append("")

    lines.append("## Note per cartella")
    lines.append("")
    lines.append("| Cartella | Note |")
    lines.append("|---|---|")
    for folder in by_folder:
        lines.append(f"| {folder} | {len(by_folder[folder])} |")
    lines.append(f"| **Totale** | **{total_notes}** |")
    lines.append("")

    lines.append("## Hub (_index per cartella)")
    lines.append("")
    for folder in by_folder:
        index_path = vault_root / folder / "_index.md"
        if index_path.is_file():
            fm, _ = parse_note(index_path)
            summary = fm.get("summary", "").strip()
            lines.append(f"- **{folder}**: {summary}")
        else:
            lines.append(f"- **{folder}**: (nessun _index.md — hub mancante)")
    lines.append("")

    content = "\n".join(lines).rstrip("\n") + "\n"

    out_dir = vault_root / "_showcase"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "showcase.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"Scritto {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
