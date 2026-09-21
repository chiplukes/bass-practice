"""Tests for song (tab) resolution."""

from __future__ import annotations

import pytest

from bass_practice.music.tab import SongError, resolve_song, validate_song


def test_resolve_open_strings() -> None:
    song = {
        "name": "Open",
        "steps": [
            {"type": "note", "string": 0, "fret": 0},
            {"type": "note", "string": 1, "fret": 0},
        ],
    }
    steps = resolve_song(song)
    assert [s.display for s in steps] == ["E0", "A0"]
    assert [s.notes[0].note_name for s in steps] == ["E2", "A2"]
    assert steps[0].notes[0].midi == 40
    assert steps[0].notes[0].frequency == pytest.approx(41.203, abs=0.01)


def test_resolve_note_names_and_rests() -> None:
    song = {
        "name": "Groove",
        "steps": [
            {"type": "note", "name": "E2"},
            {"type": "rest"},
            {"type": "note", "name": "B2"},
        ],
    }
    steps = resolve_song(song)
    assert [s.kind for s in steps] == ["note", "rest", "note"]
    assert steps[0].display == "E2"
    assert steps[1].display == "rest"
    assert steps[1].notes == ()
    assert steps[2].notes[0].midi == 47


def test_chord_resolution() -> None:
    song = {
        "name": "Chord",
        "steps": [
            {"type": "chord", "notes": [{"string": 0, "fret": 6}, {"string": 1, "fret": 4}]},
        ],
    }
    steps = resolve_song(song)
    assert len(steps) == 1
    step = steps[0]
    assert step.kind == "chord"
    assert len(step.notes) == 2
    assert [n.fret for n in step.notes] == [6, 4]
    assert step.display == "E6 A4"


def test_technique_label() -> None:
    song = {
        "name": "Tech",
        "steps": [
            {"type": "note", "string": 2, "fret": 0},
            {"type": "note", "string": 2, "fret": 2, "technique": "h"},
        ],
    }
    steps = resolve_song(song)
    assert steps[0].display == "D0"
    assert steps[1].display == "D2h"


def test_phrase_repeat() -> None:
    song = {
        "name": "Repeat",
        "steps": [
            {
                "type": "phrase",
                "repeat": 3,
                "steps": [
                    {"type": "note", "string": 0, "fret": 0},
                    {"type": "rest"},
                ],
            },
        ],
    }
    steps = resolve_song(song)
    assert [s.display for s in steps] == ["E0", "rest", "E0", "rest", "E0", "rest"]


def test_custom_tuning() -> None:
    song = {
        "name": "Drop D",
        "tuning": ["D2", "A2", "D3", "G3"],
        "steps": [{"type": "note", "string": 0, "fret": 0}],
    }
    steps = resolve_song(song)
    assert steps[0].notes[0].note_name == "D2"


def test_validate_song_missing_name() -> None:
    with pytest.raises(SongError):
        validate_song({"steps": []})


def test_validate_song_missing_steps() -> None:
    with pytest.raises(SongError):
        validate_song({"name": "No steps"})


def test_bad_step_raises() -> None:
    with pytest.raises(SongError):
        resolve_song({"name": "Bad", "steps": [{"type": "note"}]})


def test_bad_chord_raises() -> None:
    with pytest.raises(SongError):
        resolve_song({"name": "Bad chord", "steps": [{"type": "chord", "notes": []}]})
