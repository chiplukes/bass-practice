"""Flashcard deck generation: notes paired with fretboard positions."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .fretboard import Fretboard
from .notes import midi_to_note, note_to_midi


@dataclass(frozen=True)
class Flashcard:
    """A note to show, its tab position, and every fretboard position for it."""

    name: str
    midi: int
    frequency: float
    string: int  # chosen position for the tab display (0 = lowest string)
    fret: int
    positions: tuple[tuple[int, int], ...]


def generate_deck(
    start: str,
    end: str,
    max_fret: int = 12,
    seed: int | None = None,
) -> list[Flashcard]:
    """Generate one card per note in the inclusive range, with a random tab position.

    Notes with no reachable position within ``max_fret`` are skipped.
    """
    fretboard = Fretboard()
    rng = random.Random(seed)
    lo = note_to_midi(start)
    hi = note_to_midi(end)
    if hi < lo:
        lo, hi = hi, lo

    cards: list[Flashcard] = []
    for midi in range(lo, hi + 1):
        note = midi_to_note(midi)
        positions = fretboard.positions_for(note, max_fret=max_fret)
        if not positions:
            continue
        string, fret = rng.choice(positions)
        cards.append(
            Flashcard(
                name=note.name,
                midi=midi,
                frequency=note.frequency,
                string=string,
                fret=fret,
                positions=tuple(positions),
            )
        )
    return cards
