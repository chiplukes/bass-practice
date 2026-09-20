"""Tests for note math."""

from __future__ import annotations

import pytest

from bass_practice.music.notes import (
    Note,
    NoteError,
    midi_to_frequency,
    midi_to_note,
    note_to_midi,
    parse_note,
)


@pytest.mark.parametrize(
    ("text", "midi", "name"),
    [
        ("E1", 28, "E1"),
        ("A1", 33, "A1"),
        ("D2", 38, "D2"),
        ("G2", 43, "G2"),
        ("E2", 40, "E2"),
        ("C4", 60, "C4"),
        ("F#2", 42, "F#2"),
        ("Bb1", 34, "A#1"),
    ],
)
def test_note_to_midi(text: str, midi: int, name: str) -> None:
    assert note_to_midi(text) == midi
    assert parse_note(text).name == name


def test_midi_to_note_roundtrip() -> None:
    for midi in range(28, 56):
        note = midi_to_note(midi)
        assert note.midi == midi


def test_midi_to_frequency() -> None:
    assert midi_to_frequency(69) == pytest.approx(440.0)
    assert midi_to_frequency(40) == pytest.approx(82.406, abs=0.01)


def test_midi_to_frequency_matches_note() -> None:
    note = parse_note("E2")
    assert note.frequency == pytest.approx(midi_to_frequency(note.sounding_midi))


def test_bass_sounds_an_octave_below_written() -> None:
    note = parse_note("E2")
    assert note.sounding_midi == note.midi - 12
    # Open E is written as E2 but sounds at ~41 Hz (E1).
    assert note.frequency == pytest.approx(41.203, abs=0.01)


def test_transpose() -> None:
    assert parse_note("E2").transposed(12).name == "E3"
    assert parse_note("E2").transposed(7).name == "B2"


def test_invalid_note_raises() -> None:
    with pytest.raises(NoteError):
        parse_note("H2")
    with pytest.raises(NoteError):
        parse_note("E")
    with pytest.raises(NoteError):
        parse_note("not a note")


def test_note_is_hashable_and_frozen() -> None:
    note = Note(letter="E", accidental="", octave=2)
    assert {note: 1}[note] == 1


def test_math_import_is_unused_guard() -> None:
    # frequency_to_midi inverts midi_to_frequency for bass range
    from bass_practice.music.notes import frequency_to_midi

    assert frequency_to_midi(midi_to_frequency(40)) == 40
