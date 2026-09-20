"""Tests for flashcard deck generation."""

from __future__ import annotations

from bass_practice.music.flashcards import generate_deck
from bass_practice.music.fretboard import Fretboard


def test_deck_covers_range() -> None:
    cards = generate_deck("E2", "A2")
    assert [c.name for c in cards] == ["E2", "F2", "F#2", "G2", "G#2", "A2"]


def test_chosen_position_resolves_to_note() -> None:
    fb = Fretboard()
    cards = generate_deck("E2", "E4", max_fret=12)
    for card in cards:
        assert fb.note_at(card.string, card.fret).name == card.name


def test_positions_are_all_valid() -> None:
    fb = Fretboard()
    cards = generate_deck("E2", "E4", max_fret=12)
    for card in cards:
        assert (card.string, card.fret) in card.positions
        for string, fret in card.positions:
            assert fb.note_at(string, fret).name == card.name


def test_max_fret_zero_only_open_strings() -> None:
    cards = generate_deck("E2", "G3", max_fret=0)
    assert [c.name for c in cards] == ["E2", "A2", "D3", "G3"]


def test_seed_reproducible() -> None:
    a = generate_deck("E2", "G3", max_fret=12, seed=3)
    b = generate_deck("E2", "G3", max_fret=12, seed=3)
    assert [(c.name, c.string, c.fret) for c in a] == [(c.name, c.string, c.fret) for c in b]
