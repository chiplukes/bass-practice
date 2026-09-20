# Architecture

## Overview

bass-practice is a client/server web app. The server is Python (FastAPI) and
owns all musical knowledge; the client is a single static page (vanilla JS) that
owns the clock and the audio. The split exists because the app's core features
are latency-sensitive (flashcards with configurable timing, immediate note
playback, interactive trainers), which favours running timing and audio in the
browser, while everything that can be reasoned about — note math, fretboard
geometry, tab parsing, interval generation — belongs in a tested Python package.

```
Browser (Web Audio + JS)          Python (FastAPI)
------------------------          --------------------------------
timing loop                       note/fretboard/interval math
note synthesis (oscillators)      tab parsing -> resolved steps
UI rendering                      song catalog -> JSON
                                  HTTP API (pre-computed data)
```

The frontend never does music theory: it only renders data the backend already
computed and plays the MIDI/frequency values it was given.

## Module layout

```
src/bass_practice/
├── __init__.py          # re-exports __version__
├── _version.py          # single source of truth for the version
├── __main__.py          # CLI entry point (uvicorn host/port)
├── app.py               # FastAPI app factory; mounts API + static
├── catalog.py           # load bundled songs from package data
├── music/               # pure Python domain (no web/audio deps)
│   ├── notes.py         # Note, MIDI <-> name, frequency conversion
│   ├── fretboard.py     # string/fret <-> note mapping
│   ├── tab.py           # song JSON -> resolved playable steps
│   ├── intervals.py     # interval name <-> semitones
│   └── ear.py           # ear-training exercise generation
├── api/                 # FastAPI routers + Pydantic schemas
│   ├── schemas.py       # request/response models
│   ├── music.py         # /api/notes, /api/intervals, /api/fretboard, /api/ear/exercise
│   └── songs.py         # /api/songs, /api/songs/{id}
├── songs/               # bundled song JSON documents
└── static/              # frontend (served verbatim)
    ├── index.html
    ├── app.js           # views + controllers
    ├── audio.js         # Web Audio synthesizer
    └── style.css
```

## Data flow

1. The browser requests pre-computed data from the API (note ranges, fretboard
   layout, resolved song steps, ear exercises).
2. The API routers translate HTTP into calls to `music/` and return Pydantic
   models serialized as JSON.
3. The frontend renders the data and drives timing via `setTimeout` loops,
   calling `BassAudio.playMidi(midi)` to synthesize each note.

The domain package `music/` imports nothing from `api/`, `catalog.py`, or
FastAPI, which is what keeps it unit-testable in isolation.

## Key design decisions

- **Audio synthesis, not samples.** `audio.js` builds a triangle-wave oscillator
  with a short attack/release envelope from a MIDI number. This gives instant
  playback of any pitch with zero assets. Real samples can be layered in later
  without changing the API (the frequency/MIDI contract stays the same).
- **Pre-resolved steps.** `tab.py` turns raw song steps (which may be notes by
  name or by string/fret, or rests) into `ResolvedStep` objects carrying
  `midi`, `frequency`, `note_name`, and a `display` label. The frontend never
  parses music notation.
- **Sharp-spelling canonicalization.** All notes are stored canonically in sharp
  spelling (`Bb1` == `A#1`). This keeps equality and hashing trivial; a future
  enhancement could preserve the user's preferred spelling for display.
