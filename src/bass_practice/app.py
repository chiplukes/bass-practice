"""FastAPI application factory for bass-practice."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from ._version import __version__
from .api import music_router, songs_router

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Build the FastAPI app, wiring API routers and the static frontend."""
    app = FastAPI(
        title="bass-practice",
        version=__version__,
        description="Practice bass: flashcards, song sequences, fretboard and ear training.",
    )

    @app.middleware("http")
    async def no_cache(request: Request, call_next):
        response = await call_next(request)
        if not request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, max-age=0"
        return response

    app.include_router(music_router, prefix="/api")
    app.include_router(songs_router, prefix="/api")

    @app.get("/api/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
