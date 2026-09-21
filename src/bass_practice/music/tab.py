"""Song sequence parsing and resolution into playable steps.

A song is a JSON document (see ``songs/``) describing a sequence of steps. A
step may be:

- a note by ``name`` (``{"type": "note", "name": "A2"}``),
- a note by ``string``/``fret`` (``{"type": "note", "string": 0, "fret": 5}``),
- a chord of simultaneous notes (``{"type": "chord", "notes": [{...}, ...]}``),
- a rest (``{"type": "rest"}``),
- a repeated sub-sequence (``{"type": "phrase", "repeat": 4, "steps": [...]}``).

Any note may carry a ``technique`` label ("h", "~", "/", "p", ...) shown in the
tab display. This module resolves the raw steps into :class:`ResolvedStep`
objects with pre-computed MIDI, frequency, note name, and display labels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .fretboard import Fretboard
from .notes import parse_note

DEFAULT_TUNING: tuple[str, ...] = ("E2", "A2", "D3", "G3")


class SongError(ValueError):
    """Raised when a song document is malformed."""


@dataclass(frozen=True)
class ResolvedNote:
    """A single resolved pitch within a step."""

    note_name: str
    midi: int
    frequency: float
    string: int | None = None
    fret: int | None = None
    technique: str | None = None


@dataclass(frozen=True)
class ResolvedStep:
    """A single playable step in a song (note, chord, or rest)."""

    kind: str  # "note" | "chord" | "rest"
    display: str
    notes: tuple[ResolvedNote, ...] = ()
    technique: str | None = None


def _resolve_note(step: dict[str, Any], fretboard: Fretboard) -> ResolvedNote:
    technique = step.get("technique")
    if "name" in step:
        note = parse_note(str(step["name"]))
        return ResolvedNote(
            note_name=note.name,
            midi=note.midi,
            frequency=note.frequency,
            technique=technique,
        )
    if "string" in step and "fret" in step:
        string = int(step["string"])
        fret = int(step["fret"])
        note = fretboard.note_at(string, fret)
        return ResolvedNote(
            note_name=note.name,
            midi=note.midi,
            frequency=note.frequency,
            string=string,
            fret=fret,
            technique=technique,
        )
    raise SongError(f"Note must have 'name', or 'string' and 'fret': {step!r}")


def _note_display(note: ResolvedNote, fretboard: Fretboard) -> str:
    if note.string is not None and note.fret is not None:
        base = fretboard.label(note.string, note.fret)
    else:
        base = note.note_name
    return base + (note.technique or "")


def resolve_step(step: dict[str, Any], fretboard: Fretboard) -> list[ResolvedStep]:
    """Resolve one raw step dict into a list of playable steps.

    Phrase steps expand to multiple steps (repeated), so the return value is a
    list. A note or chord yields a single step.
    """
    kind = step.get("type", "note")
    technique = step.get("technique")

    if kind == "rest":
        return [ResolvedStep(kind="rest", display="rest")]

    if kind == "phrase":
        repeat = int(step.get("repeat", 1))
        inner = step.get("steps")
        if not isinstance(inner, list):
            raise SongError("Phrase 'steps' must be a list")
        resolved = resolve_steps(inner, fretboard)
        return resolved * repeat

    if kind == "chord":
        notes = step.get("notes")
        if not isinstance(notes, list) or not notes:
            raise SongError("Chord 'notes' must be a non-empty list")
        resolved_notes = [_resolve_note(n, fretboard) for n in notes]
        display = " ".join(_note_display(n, fretboard) for n in resolved_notes) + (technique or "")
        return [ResolvedStep(kind="chord", display=display, notes=tuple(resolved_notes), technique=technique)]

    note = _resolve_note(step, fretboard)
    display = _note_display(note, fretboard)
    return [ResolvedStep(kind="note", display=display, notes=(note,), technique=technique)]


def resolve_steps(steps: list[dict[str, Any]], fretboard: Fretboard) -> list[ResolvedStep]:
    """Resolve a list of raw steps, flattening any phrase expansions."""
    resolved: list[ResolvedStep] = []
    for step in steps:
        resolved.extend(resolve_step(step, fretboard))
    return resolved


def resolve_song(song: dict[str, Any]) -> list[ResolvedStep]:
    """Resolve every step in a song document into playable steps."""
    tuning = tuple(song.get("tuning", DEFAULT_TUNING))
    fretboard = Fretboard(tuning=tuning)
    raw_steps = song.get("steps")
    if not isinstance(raw_steps, list):
        raise SongError("Song 'steps' must be a list")
    return resolve_steps(raw_steps, fretboard)


def validate_song(song: dict[str, Any]) -> None:
    """Validate the top-level shape of a song document, raising :class:`SongError`."""
    if not isinstance(song, dict):
        raise SongError("Song must be a JSON object")
    if not song.get("name"):
        raise SongError("Song is missing 'name'")
    resolve_song(song)
