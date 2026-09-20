"""Tests for flashcard deck generation."""

from __future__ import annotations

from bass_practice.music.flashcards import generate_deck
from bass_practice.music.fretboard import Fretboard


def test_deck_covers_range() -> None:
    cards = generate_deck("E1", "A1")
    assert [c.name for c in cards] == ["E1", "F1", "F#1", "G1", "G#1", "A1"]


def test_chosen_position_resolves_to_note() -> None:
    fb = Fretboard()
    cards = generate_deck("E1", "E4", max_fret=12)
    for card in cards:
        assert fb.note_at(card.string, card.fret).name == card.name


def test_positions_are_all_valid() -> None:
    fb = Fretboard()
    cards = generate_deck("E1", "E4", max_fret=12)
    for card in cards:
        assert (card.string, card.fret) in card.positions
        for string, fret in card.positions:
            assert fb.note_at(string, fret).name == card.name


def test_max_fret_zero_only_open_strings() -> None:
    cards = generate_deck("E1", "G2", max_fret=0)
    assert [c.name for c in cards] == ["E1", "A1", "D2", "G2"]


def test_seed_reproducible() -> None:
    a = generate_deck("E1", "G2", max_fret=12, seed=3)
    b = generate_deck("E1", "G2", max_fret=12, seed=3)
    assert [(c.name, c.string, c.fret) for c in a] == [(c.name, c.string, c.fret) for c in b]
