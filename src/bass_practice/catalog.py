"""Song catalog: load song documents bundled with the package."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


def _songs_dir() -> Any:
    return resources.files("bass_practice") / "songs"


def list_song_ids() -> list[str]:
    """Return the sorted IDs (filename stems) of bundled songs."""
    root = _songs_dir()
    return sorted(path.stem for path in root.iterdir() if path.suffix == ".json")


def load_song(song_id: str) -> dict[str, Any] | None:
    """Load a bundled song by ID, or ``None`` if it does not exist."""
    path = _songs_dir() / f"{song_id}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_songs() -> list[dict[str, Any]]:
    """Load every bundled song."""
    songs: list[dict[str, Any]] = []
    for song_id in list_song_ids():
        song = load_song(song_id)
        if song is not None:
            songs.append(song)
    return songs
