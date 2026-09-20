"""Song sequence parsing and resolution into playable steps.

A song is a JSON document (see ``songs/``) describing a sequence of steps.
Each step is either a note (by ``name`` or by ``string``/``fret``) or a rest.
This module resolves the raw steps into :class:`ResolvedStep` objects that carry
pre-computed MIDI, frequency, note name, and a display label ready for the
frontend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .fretboard import Fretboard
from .notes import parse_note

DEFAULT_TUNING: tuple[str, ...] = ("E1", "A1", "D2", "G2")


class SongError(ValueError):
    """Raised when a song document is malformed."""


@dataclass(frozen=True)
class ResolvedStep:
    """A single playable step in a song."""

    kind: str  # "note" | "rest"
    display: str
    midi: int | None = None
    frequency: float | None = None
    note_name: str | None = None


def resolve_step(step: dict[str, Any], fretboard: Fretboard) -> ResolvedStep:
    """Resolve one raw step dict into a :class:`ResolvedStep`."""
    kind = step.get("type", "note")
    if kind == "rest":
        return ResolvedStep(kind="rest", display="rest")

    if "name" in step:
        note = parse_note(str(step["name"]))
        return ResolvedStep(
            kind="note",
            display=note.name,
            midi=note.midi,
            frequency=note.frequency,
            note_name=note.name,
        )

    if "string" in step and "fret" in step:
        string = int(step["string"])
        fret = int(step["fret"])
        note = fretboard.note_at(string, fret)
        return ResolvedStep(
            kind="note",
            display=fretboard.label(string, fret),
            midi=note.midi,
            frequency=note.frequency,
            note_name=note.name,
        )

    raise SongError(f"Step must be a rest, or have 'name', or 'string' and 'fret': {step!r}")


def resolve_song(song: dict[str, Any]) -> list[ResolvedStep]:
    """Resolve every step in a song document into playable steps."""
    tuning = tuple(song.get("tuning", DEFAULT_TUNING))
    fretboard = Fretboard(tuning=tuning)
    raw_steps = song.get("steps")
    if not isinstance(raw_steps, list):
        raise SongError("Song 'steps' must be a list")
    return [resolve_step(step, fretboard) for step in raw_steps]


def validate_song(song: dict[str, Any]) -> None:
    """Validate the top-level shape of a song document, raising :class:`SongError`."""
    if not isinstance(song, dict):
        raise SongError("Song must be a JSON object")
    if not song.get("name"):
        raise SongError("Song is missing 'name'")
    resolve_song(song)
