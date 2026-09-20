# Developer Guide

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager + environment).
- A modern browser (for Web Audio).

## Setup

```bash
uv sync --extra dev
uvx pre-commit install   # one-time, activates ruff/mypy commit hooks
```

## Run the app

```bash
uv run bass-practice --host 0.0.0.0 --port 8000
```

`--reload` enables uvicorn auto-reload for development. The app binds
`0.0.0.0` by default so other devices on your LAN can reach it.

## Common tasks

| Task | Command |
|------|---------|
| Run all tests | `uv run pytest --tb=short -q` |
| Run one test file | `uv run pytest tests/test_music/test_notes.py -q` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Type check | `uv run mypy src/bass_practice/` |

## Adding a song

Drop a JSON file in `src/bass_practice/songs/` following the format in the
README. Steps may be notes by `name` (`"A1"`) or by `string`/`fret`
(`{"string": 0, "fret": 5}`), or rests (`{"type": "rest"}`). The filename stem
becomes the song ID.

## Adding a domain feature

1. Put the logic in `src/bass_practice/music/` as a pure-Python module (no
   FastAPI, no audio imports).
2. Unit-test it in `tests/test_music/`.
3. If it needs to reach the browser, add a Pydantic schema in `api/schemas.py`
   and a route in the appropriate `api/*.py` router.
4. Consume it from `static/app.js`; do all timing with `setTimeout` and all
   audio with `BassAudio.playMidi`.

## Conventions

- Line length 120; format with `ruff format`.
- Types are enforced with mypy for `src/bass_practice/` (tests are excluded).
- Notes are canonicalized to sharp spelling internally.
- Frontend has no build step; keep it plain JS, no frameworks, unless a feature
  clearly outgrows it (see roadmap).

## VexFlow 5 gotchas

`notation.js` renders standard notation with the vendored VexFlow 5 build. Two
VexFlow 5 API details that differ from older VexFlow:

- Notes must be drawn through a `Voice` + `Formatter` (drawing a `StaveNote`
  directly throws `NoTickContext: Can't getAbsoluteX()`).
- The `Voice` constructor takes camelCase options (`{ numBeats, beatValue }`);
  the old snake_case keys (`num_beats`) are silently ignored and leave the voice
  incomplete.
- `StaveNote` needs `clef: "bass"` or it is positioned as treble.

To iterate on the frontend headlessly, a browser is required; the project has no
Playwright setup, but any Chromium can be pointed at a running server to capture
`pageerror`/console output.
