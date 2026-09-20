"""Ear-training exercise generation."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .intervals import validate_interval
from .notes import midi_to_note


@dataclass(frozen=True)
class IntervalQuestion:
    """One ear-training question: two pitches and the interval between them."""

    interval: str
    semitones: int
    low_midi: int
    high_midi: int
    low_note: str
    high_note: str


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
            )
        )
    return questions
