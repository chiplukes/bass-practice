# bass-practice

A locally-served web app for practicing bass guitar. Open it on any device on
your network and practice with four tools:

- **Flashcards** — a note is shown for a configurable time, then played. Each
  card can display the note name, tablature, and/or standard bass-clef
  notation (each independently toggleable), plus an optional fretboard that
  marks the note's positions.
- **Song player** — load a sequence of tabs and play through it at any speed.
- **Fretboard trainer** — name the note, find it on the fretboard.
- **Ear trainer** — identify intervals by ear.

Audio is synthesized in the browser with the Web Audio API (no samples needed).
All musical logic (note math, fretboard mapping, tab parsing, interval
generation) lives in a small, well-tested Python package.

## Quick start

```bash
uv sync --extra dev
uv run bass-practice --host 0.0.0.0 --port 8000
```

Then open <http://localhost:8000> (or `http://<your-ip>:8000` from another
device on the network).

## Development

```bash
uv sync --extra dev
uv run pytest --tb=short -q     # run tests
uv run ruff check .             # lint
uv run mypy src/bass_practice/  # type check
```

See `notes/` for architecture, roadmap, and developer documentation.

## Adding songs

Songs are JSON documents in `src/bass_practice/songs/`. A step is either a note
(by `name` or by `string`/`fret`) or a rest:

```json
{
  "name": "Example",
  "bpm": 100,
  "tuning": ["E2", "A2", "D3", "G3"],
  "steps": [
    { "type": "note", "string": 0, "fret": 0 },
    { "type": "note", "name": "A2" },
    { "type": "note", "string": 2, "fret": 2, "technique": "h" },
    { "type": "chord", "notes": [{ "string": 0, "fret": 6 }, { "string": 1, "fret": 4 }] },
    { "type": "phrase", "repeat": 4, "steps": [ { "type": "note", "string": 1, "fret": 2 } ] },
    { "type": "rest" }
  ]
}
```

Supported step types:

- `note` by `name` or by `string`/`fret` (optional `technique` label: `"h"`,
  `"~"`, `"slide"`, `"p"`, ...).
- `chord` — simultaneous notes (`notes` list), played together.
- `phrase` — repeat a sub-sequence `repeat` times.
- `rest`.

Notes follow standard bass notation: the bass is a transposing instrument, so
pitches are written an octave higher than they sound (open E is written `E2` but
sounds at ~41 Hz).

## License

MIT
