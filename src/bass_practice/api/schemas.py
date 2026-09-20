"""Pydantic response/request models for the JSON API."""

from __future__ import annotations

from pydantic import BaseModel


class NoteInfo(BaseModel):
    name: str
    midi: int
    frequency: float


class NotesResponse(BaseModel):
    notes: list[NoteInfo]


class PositionInfo(BaseModel):
    string: int
    fret: int


class FlashcardInfo(BaseModel):
    name: str
    midi: int
    frequency: float
    string: int
    fret: int
    positions: list[PositionInfo]


class FlashcardsResponse(BaseModel):
    cards: list[FlashcardInfo]


class StepInfo(BaseModel):
    kind: str
    display: str
    midi: int | None = None
    frequency: float | None = None
    note_name: str | None = None


class SongSummary(BaseModel):
    id: str
    name: str
    description: str = ""
    bpm: int = 120
    step_count: int


class SongDetail(SongSummary):
    tuning: list[str]
    steps: list[StepInfo]


class SongsResponse(BaseModel):
    songs: list[SongSummary]


class FretboardResponse(BaseModel):
    tuning: list[str]
    string_labels: list[str]
    max_fret: int
    layout: list[list[str]]


class EarExerciseRequest(BaseModel):
    intervals: list[str]
    root: str = "E2"
    count: int = 8
    descending: bool = False
    seed: int | None = None


class IntervalQuestionInfo(BaseModel):
    interval: str
    semitones: int
    low_midi: int
    high_midi: int
    low_note: str
    high_note: str
    low_frequency: float
    high_frequency: float


class EarExerciseResponse(BaseModel):
    root: str
    questions: list[IntervalQuestionInfo]
