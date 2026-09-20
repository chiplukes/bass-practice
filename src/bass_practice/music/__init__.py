"""Music theory domain: notes, fretboard, tab parsing, and intervals."""

from .ear import IntervalQuestion, generate_exercise
from .flashcards import Flashcard, generate_deck
from .fretboard import STANDARD_TUNING, Fretboard
from .intervals import INTERVALS, validate_interval
from .notes import Note, NoteError, midi_to_frequency, midi_to_note, note_to_midi, parse_note
from .tab import DEFAULT_TUNING, ResolvedStep, SongError, resolve_song, validate_song

__all__ = [
    "DEFAULT_TUNING",
    "Flashcard",
    "Fretboard",
    "INTERVALS",
    "IntervalQuestion",
    "Note",
    "NoteError",
    "ResolvedStep",
    "STANDARD_TUNING",
    "SongError",
    "generate_deck",
    "generate_exercise",
    "midi_to_frequency",
    "midi_to_note",
    "note_to_midi",
    "parse_note",
    "resolve_song",
    "validate_interval",
    "validate_song",
]
