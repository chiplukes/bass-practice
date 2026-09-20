"""Tests for the fretboard model."""

from __future__ import annotations

import pytest

from bass_practice.music.fretboard import Fretboard


def test_open_string_notes() -> None:
    fb = Fretboard()
    assert fb.note_at(0, 0).name == "E1"
    assert fb.note_at(1, 0).name == "A1"
    assert fb.note_at(2, 0).name == "D2"
    assert fb.note_at(3, 0).name == "G2"


def test_fifth_fret_equals_next_string() -> None:
    fb = Fretboard()
    assert fb.note_at(0, 5).name == "A1"
    assert fb.note_at(1, 5).name == "D2"
    assert fb.note_at(2, 5).name == "G2"


def test_positions_for() -> None:
    fb = Fretboard()
    assert fb.positions_for("E1") == [(0, 0)]
    assert fb.positions_for("A1") == [(0, 5), (1, 0)]


def test_positions_respect_max_fret() -> None:
    fb = Fretboard()
    assert fb.positions_for("A1", max_fret=3) == [(1, 0)]


def test_label() -> None:
    fb = Fretboard()
    assert fb.label(0, 0) == "E0"
    assert fb.label(1, 2) == "A2"


def test_layout_shape() -> None:
    fb = Fretboard()
    layout = fb.layout(max_fret=12)
    assert len(layout) == 4
    assert all(len(row) == 13 for row in layout)
    assert layout[0][0] == "E1"


def test_invalid_string_raises() -> None:
    fb = Fretboard()
    with pytest.raises(ValueError):
        fb.note_at(4, 0)
    with pytest.raises(ValueError):
        fb.note_at(0, -1)
