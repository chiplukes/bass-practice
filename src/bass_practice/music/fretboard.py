"""Fretboard model: map between strings, frets, and notes for the bass."""

from __future__ import annotations

from dataclasses import dataclass

from .notes import Note, midi_to_note, note_to_midi

# Standard 4-string bass tuning, low to high (E1 == MIDI 28).
STANDARD_TUNING: tuple[str, ...] = ("E1", "A1", "D2", "G2")


@dataclass(frozen=True)
class Fretboard:
    """A bass fretboard with a given tuning.

    Strings are indexed ``0..n-1`` from lowest to highest pitch. Frets are
    ``0`` (open string) up to ``max_fret``.
    """

    tuning: tuple[str, ...] = STANDARD_TUNING

    @property
    def string_midis(self) -> tuple[int, ...]:
        return tuple(note_to_midi(t) for t in self.tuning)

    @property
    def string_labels(self) -> tuple[str, ...]:
        return tuple(t[0] for t in self.tuning)

    def note_at(self, string: int, fret: int) -> Note:
        """Return the :class:`Note` sounded at a given string and fret."""
        if not 0 <= string < len(self.string_midis):
            raise ValueError(f"String index out of range: {string}")
        if fret < 0:
            raise ValueError(f"Fret must be non-negative: {fret}")
        return midi_to_note(self.string_midis[string] + fret)

    def positions_for(self, note: Note | str, max_fret: int = 12) -> list[tuple[int, int]]:
        """Return ``(string, fret)`` positions where *note* can be played.

        Positions are listed lowest-string-first. ``max_fret`` bounds the
        returned frets (inclusive).
        """
        target = note.midi if isinstance(note, Note) else note_to_midi(note)
        positions: list[tuple[int, int]] = []
        for string, base in enumerate(self.string_midis):
            fret = target - base
            if 0 <= fret <= max_fret:
                positions.append((string, fret))
        return positions

    def label(self, string: int, fret: int) -> str:
        """Short tab label for a position, e.g. ``"E0"`` or ``"A2"``."""
        return f"{self.string_labels[string]}{fret}"

    def layout(self, max_fret: int = 12) -> list[list[str]]:
        """Return a ``[string][fret]`` grid of note names for the trainer."""
        return [[self.note_at(string, fret).name for fret in range(max_fret + 1)] for string in range(len(self.tuning))]
