"""Note, fretboard, and ear-training endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..music import (
    INTERVALS,
    Fretboard,
    generate_deck,
    generate_exercise,
    midi_to_note,
    note_to_midi,
    validate_interval,
)
from .schemas import (
    EarExerciseRequest,
    EarExerciseResponse,
    FlashcardInfo,
    FlashcardsResponse,
    FretboardResponse,
    IntervalQuestionInfo,
    NoteInfo,
    NotesResponse,
    PositionInfo,
)

router = APIRouter(tags=["music"])


@router.get("/notes", response_model=NotesResponse)
def list_notes(start: str = "E2", end: str = "G3") -> NotesResponse:
    """List every note (with MIDI and sounding frequency) in an inclusive pitch range."""
    lo = note_to_midi(start)
    hi = note_to_midi(end)
    if hi < lo:
        lo, hi = hi, lo
    notes = []
    for midi in range(lo, hi + 1):
        note = midi_to_note(midi)
        notes.append(NoteInfo(name=note.name, midi=note.midi, frequency=note.frequency))
    return NotesResponse(notes=notes)


@router.get("/intervals", response_model=list[str])
def list_intervals() -> list[str]:
    """List the supported ear-training interval names."""
    return list(INTERVALS)


@router.get("/flashcards", response_model=FlashcardsResponse)
def flashcards(start: str = "E2", end: str = "G3", max_fret: int = 12) -> FlashcardsResponse:
    """Generate a flashcard deck: each card is a note plus its fretboard positions."""
    cards = generate_deck(start, end, max_fret=max_fret)
    return FlashcardsResponse(
        cards=[
            FlashcardInfo(
                name=c.name,
                midi=c.midi,
                frequency=c.frequency,
                string=c.string,
                fret=c.fret,
                positions=[PositionInfo(string=s, fret=f) for s, f in c.positions],
            )
            for c in cards
        ]
    )


@router.get("/fretboard", response_model=FretboardResponse)
def get_fretboard(max_fret: int = 12) -> FretboardResponse:
    """Return the standard bass fretboard layout as a ``[string][fret]`` grid."""
    fretboard = Fretboard()
    return FretboardResponse(
        tuning=list(fretboard.tuning),
        string_labels=list(fretboard.string_labels),
        max_fret=max_fret,
        layout=fretboard.layout(max_fret=max_fret),
    )


@router.post("/ear/exercise", response_model=EarExerciseResponse)
def ear_exercise(req: EarExerciseRequest) -> EarExerciseResponse:
    """Generate an ear-training exercise of random intervals from a root pitch."""
    try:
        for name in req.intervals:
            validate_interval(name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    root_midi = note_to_midi(req.root)
    questions = generate_exercise(
        req.intervals,
        root_midi,
        req.count,
        seed=req.seed,
        descending=req.descending,
    )
    return EarExerciseResponse(
        root=req.root,
        questions=[
            IntervalQuestionInfo(
                interval=q.interval,
                semitones=q.semitones,
                low_midi=q.low_midi,
                high_midi=q.high_midi,
                low_note=q.low_note,
                high_note=q.high_note,
                low_frequency=q.low_frequency,
                high_frequency=q.high_frequency,
            )
            for q in questions
        ],
    )
