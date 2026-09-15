#!/usr/bin/env python3
"""Genera llms.txt alla radice del vault: l'indice-porta per le AI.

llms.txt e' DERIVATO: questo script lo rigenera da capo ogni volta a partire
dal frontmatter delle note. Non va mai modificato a mano.

Per ogni cartella di contenuto (self, areas, projects, concepts, docs,
entities, data, code, outputs) elenca le sue note come:
    - [[nome-file]] -- summary
prendendo title/summary SOLO dal frontmatter di ciascuna nota. sources/ e
workspace/ sono escluse.

Uso:
    python3 generate_llms_txt.py [percorso_vault]
"""

from __future__ import annotations

import sys
from pathlib import Path

CONTENT_FOLDERS = [
    "self",
    "areas",
    "projects",
    "concepts",
    "docs",
    "entities",
    "data",
    "code",
    "outputs",
]


def parse_frontmatter(path: Path) -> dict[str, str]:
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
    return fm


def build_llms_txt(vault_root: Path) -> str:
    out = []
    out.append("# llms.txt — Cervello Aziendale")
    out.append("")
    out.append(
        "> File DERIVATO, generato da `code/generate_llms_txt.py` a partire dal "
        "frontmatter delle note. Non modificarlo a mano: rigeneralo da capo "
        "eseguendo lo script."
    )
    out.append("")

    for folder in CONTENT_FOLDERS:
        folder_path = vault_root / folder
        out.append(f"## {folder}")
        if not folder_path.is_dir():
            out.append("(cartella assente)")
            out.append("")
            continue
        note_paths = sorted(folder_path.rglob("*.md"), key=lambda p: p.relative_to(folder_path).as_posix())
        if not note_paths:
            out.append("(nessuna nota)")
            out.append("")
            continue
        for path in note_paths:
            fm = parse_frontmatter(path)
            summary = fm.get("summary", "").strip()
            out.append(f"- [[{path.stem}]] -- {summary}")
        out.append("")

    return "\n".join(out).rstrip("\n") + "\n"


def main():
    vault_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    content = build_llms_txt(vault_root)
    out_path = vault_root / "llms.txt"
    out_path.write_text(content, encoding="utf-8")
    print(f"Scritto {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
