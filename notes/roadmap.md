# Roadmap

## Done

- Project scaffold (uv, src layout, ruff/mypy/pre-commit/pytest, CI).
- `music/` domain: notes, fretboard, tab parsing, intervals, ear exercises.
- FastAPI app serving a JSON API and static frontend.
- Frontend with four thin slices: flashcards, song player, fretboard trainer,
  ear trainer.
- Three bundled example songs.

## Near-term

- **User songs directory.** Load songs from a local directory (env var or
  `--songs-dir`) in addition to bundled package data, so users can add their own
  songs without reinstalling.
- **Flashcard modes.** Flash string/fret position (tab) in addition to note
  names, and a "show then you must name it before playback" mode.
- **Ear trainer direction.** Randomize ascending/descending per question.
- **Scoring/persistence.** Persist fretboard and ear trainer scores locally.
- **Real sample playback.** Optional sampled bass timbre layered on top of (or
  replacing) synthesis, selected per tool.

## Later

- **Staff notation.** Render notes on a musical staff (SVG) for flashcards.
- **Tuner.** A chromatic tuner using microphone input.
- **Chord / interval dictation.** Extend the ear trainer beyond single intervals.
- **MIDI input.** Drive the fretboard trainer from a MIDI controller.
- **Custom tunings / 5-6 string basses.** Generalize `Fretboard` further and
  expose tuning selection in the UI.

## Non-goals (for now)

- Accounts, cloud sync, or any multi-user backend. The app is single-user and
  LAN-local by design.
