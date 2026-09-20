"""Song catalog endpoints."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from ..catalog import list_song_ids, load_song
from ..music import DEFAULT_TUNING, resolve_song
from .schemas import SongDetail, SongsResponse, SongSummary, StepInfo

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("", response_model=SongsResponse)
def list_songs() -> SongsResponse:
    """List all bundled songs (summaries only)."""
    summaries: list[SongSummary] = []
    for song_id in list_song_ids():
        song = load_song(song_id)
        if song is None:
            continue
        summaries.append(
            SongSummary(
                id=song_id,
                name=song["name"],
                description=song.get("description", ""),
                bpm=song.get("bpm", 120),
                step_count=len(song.get("steps", [])),
            )
        )
    return SongsResponse(songs=summaries)


@router.get("/{song_id}", response_model=SongDetail)
def get_song(song_id: str) -> SongDetail:
    """Return a single song with its steps fully resolved for playback."""
    song = load_song(song_id)
    if song is None:
        raise HTTPException(status_code=404, detail=f"Unknown song: {song_id}")
    steps = [StepInfo(**asdict(step)) for step in resolve_song(song)]
    return SongDetail(
        id=song_id,
        name=song["name"],
        description=song.get("description", ""),
        bpm=song.get("bpm", 120),
        step_count=len(steps),
        tuning=list(song.get("tuning", DEFAULT_TUNING)),
        steps=steps,
    )
