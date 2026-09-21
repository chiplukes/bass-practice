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
    res = client.get("/api/notes", params={"start": "E2", "end": "A2"})
    assert res.status_code == 200
    notes = res.json()["notes"]
    assert [n["name"] for n in notes] == ["E2", "F2", "F#2", "G2", "G#2", "A2"]
    assert all(n["frequency"] > 0 for n in notes)


def test_notes_reversed_range() -> None:
    res = client.get("/api/notes", params={"start": "A2", "end": "E2"})
    notes = res.json()["notes"]
    assert notes[0]["name"] == "E2"


def test_intervals() -> None:
    res = client.get("/api/intervals")
    assert res.status_code == 200
    assert "perfect 5th" in res.json()


def test_flashcards() -> None:
    res = client.get("/api/flashcards", params={"start": "E2", "end": "A2", "max_fret": 12})
    assert res.status_code == 200
    cards = res.json()["cards"]
    assert [c["name"] for c in cards] == ["E2", "F2", "F#2", "G2", "G#2", "A2"]
    assert all(c["positions"] for c in cards)
    assert all(c["string"] >= 0 and c["fret"] >= 0 for c in cards)


def test_fretboard() -> None:
    res = client.get("/api/fretboard", params={"max_fret": 12})
    assert res.status_code == 200
    body = res.json()
    assert body["layout"][0][0] == "E2"
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
    assert all(q["low_frequency"] > 0 and q["high_frequency"] > 0 for q in body["questions"])


def test_ear_exercise_bad_interval() -> None:
    res = client.post("/api/ear/exercise", json={"intervals": ["bogus"], "root": "E2", "count": 1})
    assert res.status_code == 422


def test_ear_degrees() -> None:
    res = client.post(
        "/api/ear/degrees",
        json={"root": "C3", "degrees": [1, 3, 5], "count": 5, "seed": 3},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["root"] == "C3"
    assert body["root_frequency"] > 0
    assert len(body["questions"]) == 5
    assert all(q["degree"] in {1, 3, 5} for q in body["questions"])
    assert all(q["frequency"] > 0 for q in body["questions"])


def test_ear_degrees_bad_degree() -> None:
    res = client.post("/api/ear/degrees", json={"root": "C3", "degrees": [99], "count": 1})
    assert res.status_code == 422
