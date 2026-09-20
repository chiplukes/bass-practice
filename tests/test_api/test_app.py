"""Tests for the JSON API via FastAPI's TestClient."""

from __future__ import annotations

from fastapi.testclient import TestClient

from bass_practice.app import app

client = TestClient(app)


def test_health() -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_notes_range() -> None:
    res = client.get("/api/notes", params={"start": "E1", "end": "A1"})
    assert res.status_code == 200
    notes = res.json()["notes"]
    assert [n["name"] for n in notes] == ["E1", "F1", "F#1", "G1", "G#1", "A1"]
    assert all(n["frequency"] > 0 for n in notes)


def test_notes_reversed_range() -> None:
    res = client.get("/api/notes", params={"start": "A1", "end": "E1"})
    notes = res.json()["notes"]
    assert notes[0]["name"] == "E1"


def test_intervals() -> None:
    res = client.get("/api/intervals")
    assert res.status_code == 200
    assert "perfect 5th" in res.json()


def test_fretboard() -> None:
    res = client.get("/api/fretboard", params={"max_fret": 12})
    assert res.status_code == 200
    body = res.json()
    assert body["layout"][0][0] == "E1"
    assert body["string_labels"] == ["E", "A", "D", "G"]


def test_songs_list_and_detail() -> None:
    res = client.get("/api/songs")
    assert res.status_code == 200
    songs = res.json()["songs"]
    assert songs, "expected bundled example songs"

    song_id = songs[0]["id"]
    detail = client.get(f"/api/songs/{song_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["steps"]


def test_song_not_found() -> None:
    res = client.get("/api/songs/does-not-exist")
    assert res.status_code == 404


def test_ear_exercise() -> None:
    res = client.post(
        "/api/ear/exercise",
        json={"intervals": ["perfect 5th", "major 3rd"], "root": "E2", "count": 4, "seed": 7},
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["questions"]) == 4
    assert all(q["interval"] in {"perfect 5th", "major 3rd"} for q in body["questions"])


def test_ear_exercise_bad_interval() -> None:
    res = client.post("/api/ear/exercise", json={"intervals": ["bogus"], "root": "E2", "count": 1})
    assert res.status_code == 422
