# Roadmap

## Done

- Project scaffold (uv, src layout, ruff/mypy/pre-commit/pytest, CI).
- `music/` domain: notes, fretboard, tab parsing, intervals, ear exercises.
- FastAPI app serving a JSON API and static frontend.
- Frontend with four thin slices: flashcards, song player, fretboard trainer,
  ear trainer.
- Flashcards and the song player share a study card with independently
  toggleable note name, tablature, standard bass-clef notation (VexFlow), and a
  fretboard helper that marks positions.
- Song format supports chords, technique labels (hammer-on/vibrato/slide), and
  repeated phrases. Bundled songs include scales and "It's My Life" (No Doubt).
- Global sound toggle (persisted) with a test button.
- Ear trainer is functional: play a key, then a scale degree, and identify the
  degree (Do/Re/Mi/...).
- Bundled example songs.

## Near-term

- **User songs directory.** Load songs from a local directory (env var or
  `--songs-dir`) in addition to bundled package data, so users can add their own
  songs without reinstalling.
- **Flashcard mode.** "Show then you must name it before playback" mode.
- **Scoring/persistence.** Persist fretboard and ear trainer scores locally.
- **Real sample playback.** Optional sampled bass timbre layered on top of (or
  replacing) synthesis, selected per tool.

## Later

- **Tuner.** A chromatic tuner using microphone input.
- **Chord dictation.** Extend the ear trainer to chord qualities.
- **MIDI input.** Drive the fretboard trainer from a MIDI controller.
- **Custom tunings / 5-6 string basses.** Generalize `Fretboard` further and
  expose tuning selection in the UI.

## Non-goals (for now)

- Accounts, cloud sync, or any multi-user backend. The app is single-user and
  LAN-local by design.
