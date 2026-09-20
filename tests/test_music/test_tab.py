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
    assert [s.note_name for s in steps] == ["E1", "A1"]
    assert steps[0].midi == 28


def test_resolve_note_names_and_rests() -> None:
    song = {
        "name": "Groove",
        "steps": [
            {"type": "note", "name": "E1"},
            {"type": "rest"},
            {"type": "note", "name": "B1"},
        ],
    }
    steps = resolve_song(song)
    assert [s.kind for s in steps] == ["note", "rest", "note"]
    assert steps[0].display == "E1"
    assert steps[1].display == "rest"
    assert steps[1].midi is None
    assert steps[2].midi == 35


def test_custom_tuning() -> None:
    song = {
        "name": "Drop D",
        "tuning": ["D1", "A1", "D2", "G2"],
        "steps": [{"type": "note", "string": 0, "fret": 0}],
    }
    steps = resolve_song(song)
    assert steps[0].note_name == "D1"


def test_validate_song_missing_name() -> None:
    with pytest.raises(SongError):
        validate_song({"steps": []})


def test_validate_song_missing_steps() -> None:
    with pytest.raises(SongError):
        validate_song({"name": "No steps"})


def test_bad_step_raises() -> None:
    with pytest.raises(SongError):
        resolve_song({"name": "Bad", "steps": [{"type": "note"}]})
