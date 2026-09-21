"""Parse a pasted 4-line ASCII bass tab into a song JSON.

Handles two common formats:
- Labelled lines: "G  :", "D  :", "A  :", "E  :" (plain-text tabs)
- Power Tab style: "|...|" lines, where each group of 4 lines is G/D/A/E

Usage:
    uv run python tools/import_tab_text.py tab.txt --name "Song" --bpm 110 \
        --out src/bass_practice/songs/song.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STRING_MAP = {"G": 3, "D": 2, "A": 1, "E": 0}
_LABEL_RE = re.compile(r"^\s*([GgDdAaEe])\s*:")


def _digits(content: str) -> list[tuple[int, int]]:
    return [(m.start(), int(m.group())) for m in re.finditer(r"\d+", content)]


def parse_tab(text: str) -> list[dict]:
    """Return note steps in time order, grouped by 4-line systems."""
    systems: list[list[tuple[int, int, int]]] = []
    current: list[tuple[int, int, int]] = []
    powertab_cycle = ["G", "D", "A", "E"]
    powertab_idx = 0

    for raw in text.splitlines():
        line = raw.rstrip()
        label = _LABEL_RE.match(line)
        if label:
            letter = label.group(1).upper()
            content = line[line.index(":") + 1 :]
            for pos, fret in _digits(content):
                current.append((pos, STRING_MAP[letter], fret))
            if letter == "E":
                systems.append(current)
                current = []
        elif line.startswith("|") and any(c.isdigit() for c in line):
            letter = powertab_cycle[powertab_idx % 4]
            powertab_idx += 1
            for pos, fret in _digits(line):
                current.append((pos, STRING_MAP[letter], fret))
            if powertab_idx % 4 == 0:
                systems.append(current)
                current = []

    if current:
        systems.append(current)

    steps: list[dict] = []
    for system in systems:
        system.sort(key=lambda n: (n[0], n[1]))
        steps.extend({"type": "note", "string": s, "fret": f} for _, s, f in system)
    return steps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tab", help="Path to the tab text file")
    parser.add_argument("--name", required=True)
    parser.add_argument("--bpm", type=int, default=120)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    text = Path(args.tab).read_text(encoding="utf-8")
    steps = parse_tab(text)
    song = {
        "name": args.name,
        "description": "Imported from pasted tab.",
        "bpm": args.bpm,
        "tuning": ["E2", "A2", "D3", "G3"],
        "steps": steps,
    }
    Path(args.out).write_text(json.dumps(song, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} with {len(steps)} steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
