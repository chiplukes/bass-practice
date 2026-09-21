"""Ear-training exercise generation."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .intervals import validate_interval
from .notes import midi_to_frequency, midi_to_note, written_to_sounding_midi

# Movable-do scale degrees of the major scale: degree -> (solfege, semitones).
SCALE_DEGREES: dict[int, tuple[str, int]] = {
    1: ("Do", 0),
    2: ("Re", 2),
    3: ("Mi", 4),
    4: ("Fa", 5),
    5: ("So", 7),
    6: ("La", 9),
    7: ("Ti", 11),
}


@dataclass(frozen=True)
class IntervalQuestion:
    """One ear-training question: two pitches and the interval between them."""

    interval: str
    semitones: int
    low_midi: int
    high_midi: int
    low_note: str
    high_note: str
    low_frequency: float
    high_frequency: float


def generate_exercise(
    intervals: list[str],
    root_midi: int,
    count: int,
    *,
    seed: int | None = None,
    descending: bool = False,
) -> list[IntervalQuestion]:
    """Generate *count* interval questions from a root pitch.

    By default each question sounds the root followed by the interval above it
    (ascending). Set ``descending=True`` to sound the interval below the root.
    """
    rng = random.Random(seed)
    name_by_semitone = {validate_interval(name): name for name in intervals}
    semitones = list(name_by_semitone)
    if not semitones:
        raise ValueError("At least one interval is required")

    questions: list[IntervalQuestion] = []
    for _ in range(count):
        semi = rng.choice(semitones)
        high_midi = root_midi + semi if not descending else root_midi - semi
        if descending:
            low_midi, high_midi = high_midi, root_midi
        else:
            low_midi = root_midi
        low_note = midi_to_note(low_midi)
        high_note = midi_to_note(high_midi)
        name = name_by_semitone[semi]
        questions.append(
            IntervalQuestion(
                interval=name,
                semitones=semi,
                low_midi=low_midi,
                high_midi=high_midi,
                low_note=low_note.name,
                high_note=high_note.name,
                low_frequency=midi_to_frequency(written_to_sounding_midi(low_midi)),
                high_frequency=midi_to_frequency(written_to_sounding_midi(high_midi)),
            )
        )
    return questions


@dataclass(frozen=True)
class DegreeQuestion:
    """One functional ear-training question: a scale degree in a key."""

    degree: int
    solfege: str
    semitones: int
    note: str
    midi: int
    frequency: float


def generate_degree_exercise(
    root_midi: int,
    degrees: list[int],
    count: int,
    *,
    seed: int | None = None,
) -> list[DegreeQuestion]:
    """Generate *count* functional ear-training questions from a key root.

    Each question is a random scale degree; the note is played relative to the
    tonic (the root). ``degrees`` are major-scale degree numbers 1-7.
    """
    rng = random.Random(seed)
    valid = {d: SCALE_DEGREES[d] for d in degrees if d in SCALE_DEGREES}
    if not valid:
        raise ValueError("At least one valid scale degree (1-7) is required")

    questions: list[DegreeQuestion] = []
    for _ in range(count):
        degree = rng.choice(list(valid))
        solfege, semitones = valid[degree]
        midi = root_midi + semitones
        note = midi_to_note(midi)
        questions.append(
            DegreeQuestion(
                degree=degree,
                solfege=solfege,
                semitones=semitones,
                note=note.name,
                midi=midi,
                frequency=midi_to_frequency(written_to_sounding_midi(midi)),
            )
        )
    return questions
