"""API routers for the bass-practice app."""

from .music import router as music_router
from .songs import router as songs_router

__all__ = ["music_router", "songs_router"]
