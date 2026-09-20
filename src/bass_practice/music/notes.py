"""Note, pitch, and frequency math for the bass practice app.

Everything here is pure Python (no web or audio dependencies) so it can be
unit-tested independently of the FastAPI layer and the browser frontend.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Pitch classes by natural letter name (C=0 .. B=11).
_PITCH_CLASS: dict[str, int] = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

# Canonical (sharp) spelling of each pitch class.
_SHARP_NAMES: tuple[str, ...] = (
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
)

# A4 reference pitch for frequency calculations.
_A4_MIDI = 69
_A4_FREQ = 440.0

_NOTE_RE = re.compile(r"^(?P<letter>[A-Ga-g])(?P<acc>[#b]?)(?P<oct>-?\d+)$")


class NoteError(ValueError):
    """Raised when a note name cannot be parsed."""


@dataclass(frozen=True)
class Note:
    """A specific pitch, canonicalized to sharp spelling.

    ``midi`` is the MIDI note number (C-1 == 0, middle C == 60).
    """

    letter: str
    accidental: str  # "", "#", or "b" as input; canonical name always uses "#"
    octave: int

    @property
    def pitch_class(self) -> int:
        pc = _PITCH_CLASS[self.letter.upper()]
        if self.accidental == "#":
            pc += 1
        elif self.accidental == "b":
            pc -= 1
        return pc % 12

    @property
    def midi(self) -> int:
        return (self.octave + 1) * 12 + self.pitch_class

    @property
    def name(self) -> str:
        """Canonical name using sharp spelling, e.g. ``"E2"`` or ``"A#1"``."""
        return f"{_SHARP_NAMES[self.pitch_class]}{self.octave}"

    @property
    def frequency(self) -> float:
        return midi_to_frequency(self.midi)

    def transposed(self, semitones: int) -> Note:
        return midi_to_note(self.midi + semitones)

    def __str__(self) -> str:
        return self.name


def parse_note(text: str) -> Note:
    """Parse a note name like ``"E2"``, ``"F#1"``, or ``"Bb1"`` into a :class:`Note`."""
    match = _NOTE_RE.match(text.strip())
    if match is None:
        raise NoteError(f"Invalid note name: {text!r}")
    letter = match.group("letter").upper()
    if letter not in _PITCH_CLASS:
        raise NoteError(f"Invalid note name: {text!r}")
    accidental = match.group("acc")
    octave = int(match.group("oct"))
    return Note(letter=letter, accidental=accidental, octave=octave)


def note_to_midi(text: str) -> int:
    """Return the MIDI number for a note name."""
    return parse_note(text).midi


def midi_to_note(midi: int) -> Note:
    """Return the canonical (sharp-spelled) :class:`Note` for a MIDI number."""
    octave = midi // 12 - 1
    pitch_class = midi % 12
    return Note(
        letter=_SHARP_NAMES[pitch_class][0], accidental="#" if "#" in _SHARP_NAMES[pitch_class] else "", octave=octave
    )


def midi_to_frequency(midi: int) -> float:
    """Convert a MIDI note number to a frequency in Hz (A4 == 440 Hz)."""
    return _A4_FREQ * (2.0 ** ((midi - _A4_MIDI) / 12.0))


def frequency_to_midi(frequency: float) -> int:
    """Convert a frequency in Hz to the nearest MIDI note number."""
    import math

    return int(round(_A4_MIDI + 12.0 * math.log2(frequency / _A4_FREQ)))
