"""Tests for ear-training exercise generation."""

from __future__ import annotations

import pytest

from bass_practice.music.ear import SCALE_DEGREES, generate_degree_exercise, generate_exercise
from bass_practice.music.intervals import validate_interval
from bass_practice.music.notes import note_to_midi


def test_generate_exercise_count() -> None:
    questions = generate_exercise(["perfect 5th"], 40, count=5, seed=1)
    assert len(questions) == 5
    for q in questions:
        assert q.semitones == 7
        assert q.high_midi - q.low_midi == 7


def test_generate_exercise_seed_reproducible() -> None:
    a = generate_exercise(["major 2nd", "major 3rd"], 40, count=10, seed=42)
    b = generate_exercise(["major 2nd", "major 3rd"], 40, count=10, seed=42)
    assert [q.interval for q in a] == [q.interval for q in b]


def test_descending() -> None:
    questions = generate_exercise(["perfect 4th"], 40, count=3, seed=1, descending=True)
    for q in questions:
        assert q.high_midi == 40
        assert q.high_midi - q.low_midi == 5


def test_unknown_interval_raises() -> None:
    with pytest.raises(ValueError):
        generate_exercise(["nope"], 40, count=1)


def test_validate_interval() -> None:
    assert validate_interval("octave") == 12
    with pytest.raises(ValueError):
        validate_interval("super octave")


def test_scale_degrees_are_major_scale() -> None:
    assert SCALE_DEGREES[1] == ("Do", 0)
    assert SCALE_DEGREES[3] == ("Mi", 4)
    assert SCALE_DEGREES[5] == ("So", 7)
    assert SCALE_DEGREES[7] == ("Ti", 11)


def test_generate_degree_exercise_count() -> None:
    root = note_to_midi("C3")
    questions = generate_degree_exercise(root, [1, 3, 5], count=6, seed=1)
    assert len(questions) == 6
    for q in questions:
        assert q.degree in {1, 3, 5}
        assert q.midi - root == SCALE_DEGREES[q.degree][1]


def test_generate_degree_exercise_seed_reproducible() -> None:
    a = generate_degree_exercise(40, [1, 2, 3, 4, 5, 6, 7], count=10, seed=7)
    b = generate_degree_exercise(40, [1, 2, 3, 4, 5, 6, 7], count=10, seed=7)
    assert [q.degree for q in a] == [q.degree for q in b]


def test_generate_degree_exercise_invalid_raises() -> None:
    with pytest.raises(ValueError):
        generate_degree_exercise(40, [], count=1)
    with pytest.raises(ValueError):
        generate_degree_exercise(40, [99], count=1)
