"""Import a text-based tab PDF into the bass-practice song JSON format.

Usage:
    uv run python tools/import_pdf.py INPUT.pdf --name "Song" --bpm 120

Extracts fret numbers and slide markers from a BassTabs.org-style PDF and emits
a best-effort single-voice song. Multi-track tabs are collapsed to one line;
rhythm is not preserved. Review the output before relying on it.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pymupdf

FRET_RE = re.compile(r"^\(?(\d+)\)?$")
TECHNIQUES = {"sl.", "h", "p", "b", "/", "\\"}


def extract_items(pdf_path: str) -> list[tuple[int, float, float, str]]:
    """Return (page, x, y_center, text) for fret numbers and techniques."""
    doc = pymupdf.open(pdf_path)
    items: list[tuple[int, float, float, str]] = []
    for page_idx, page in enumerate(doc):
        for w in page.get_text("words"):
            x0, y0, y1, text = w[0], w[1], w[3], w[4].strip()
            if FRET_RE.match(text) or text in TECHNIQUES:
                items.append((page_idx, x0, (y0 + y1) / 2, text))
    return items


def cluster(values: list[float], tol: float = 2.5) -> list[float]:
    """Cluster 1-D values; return cluster centers in ascending order."""
    centers: list[float] = []
    for v in sorted(values):
        if centers and v - centers[-1] <= tol:
            centers[-1] = (centers[-1] + v) / 2
        else:
            centers.append(v)
    return centers


def build_song(items: list[tuple[int, float, float, str]]) -> list[dict]:
    """Convert extracted items into ordered song steps (string + fret)."""
    steps: list[dict] = []
    for page in sorted({i[0] for i in items}):
        page_items = sorted((i for i in items if i[0] == page), key=lambda i: (i[2], i[1]))
        # string-line positions = clusters of fret-number y-centers
        fret_ys = [i[2] for i in page_items if FRET_RE.match(i[3])]
        lines = cluster(fret_ys)
        # string spacing = median small gap between consecutive lines
        gaps = [b - a for a, b in zip(lines, lines[1:], strict=False) if b - a < 10]
        if not gaps:
            continue
        spacing = sorted(gaps)[len(gaps) // 2]
        # group lines into systems (gap > spacing * 2.2)
        systems: list[list[float]] = []
        cur: list[float] = []
        for ln in lines:
            if cur and ln - cur[-1] > spacing * 2.2:
                systems.append(cur)
                cur = []
            cur.append(ln)
        if cur:
            systems.append(cur)

        for sys_lines in systems:
            if len(sys_lines) < 2:
                continue  # bar-number / tempo rows
            # bottom line = E string (index 0), spacing upward
            bottom = sys_lines[-1]
            sys_items = [
                i for i in page_items if FRET_RE.match(i[3]) and any(abs(i[2] - ln) <= 2.5 for ln in sys_lines)
            ]
            notes = []
            for _, x, y, text in sorted(sys_items, key=lambda i: i[1]):
                string = round((bottom - y) / spacing)
                if not 0 <= string <= 3:
                    continue
                fret = int(FRET_RE.match(text).group(1))
                notes.append((x, string, fret))
            # group notes that share an x-position (chord) within ~4px
            for grp in _group_by_x(notes, tol=4.0):
                if len(grp) == 1:
                    _, s, f = grp[0]
                    steps.append({"type": "note", "string": s, "fret": f})
                else:
                    steps.append({"type": "chord", "notes": [{"string": s, "fret": f} for _, s, f in grp]})
    return steps


def _group_by_x(notes: list[tuple[float, int, int]], tol: float) -> list[list[tuple[float, int, int]]]:
    groups: list[list[tuple[float, int, int]]] = []
    cur: list[tuple[float, int, int]] = []
    cur_x = 0.0
    for note in sorted(notes, key=lambda n: n[0]):
        if cur and note[0] - cur_x > tol:
            groups.append(cur)
            cur = []
        if not cur:
            cur_x = note[0]
        cur.append(note)
    if cur:
        groups.append(cur)
    return groups


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", help="Path to the tab PDF")
    parser.add_argument("--out", help="Output JSON path (default: <stem>.json)")
    parser.add_argument("--name", help="Song name")
    parser.add_argument("--bpm", type=int, default=120)
    args = parser.parse_args()

    items = extract_items(args.pdf)
    steps = build_song(items)
    out = Path(args.out) if args.out else Path(args.pdf).with_suffix(".json")
    song = {
        "name": args.name or Path(args.pdf).stem,
        "description": f"Imported from {Path(args.pdf).name} (auto; review needed).",
        "bpm": args.bpm,
        "tuning": ["E2", "A2", "D3", "G3"],
        "steps": steps,
    }
    out.write_text(json.dumps(song, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} with {len(steps)} steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
