# Getting Started

## Install and run

```bash
uv sync --extra dev
uv run bass-practice
```

Open <http://localhost:8000>. To reach the app from another device on your
network, open `http://<this-machine's-ip>:8000` (the server already binds
`0.0.0.0`).

## Using the tools

### Flashcards
Choose how long each note is shown and the note range, then press **Start**.
A note appears, then plays after the configured delay.

### Song player
Pick a song and press **Load**. Use **Play** to step through it, **Prev** /
**Next** to move manually, and adjust **tempo** and **speed** to change pace.

### Fretboard trainer
Press **New note**, then click the correct position on the fretboard. **Reveal**
shows the whole fretboard.

### Ear trainer
Tick the intervals you want to practice, choose a root note, then **New
exercise**. **Play** sounds two notes; click the interval you heard. Correct
answers are tallied.

## Notes on audio

Audio is synthesized in the browser, so there is nothing to install. The first
click unlocks the AudioContext (a browser requirement); after that, playback
is instant.
