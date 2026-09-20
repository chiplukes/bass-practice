"""Interval definitions for the ear trainer."""

from __future__ import annotations

# Display name -> number of semitones.
INTERVALS: dict[str, int] = {
    "unison": 0,
    "minor 2nd": 1,
    "major 2nd": 2,
    "minor 3rd": 3,
    "major 3rd": 4,
    "perfect 4th": 5,
    "tritone": 6,
    "perfect 5th": 7,
    "minor 6th": 8,
    "major 6th": 9,
    "minor 7th": 10,
    "major 7th": 11,
    "octave": 12,
}


def validate_interval(name: str) -> int:
    """Return the semitone count for an interval name, raising ``ValueError`` if unknown."""
    try:
        return INTERVALS[name]
    except KeyError:
        valid = ", ".join(INTERVALS)
        raise ValueError(f"Unknown interval {name!r}; valid intervals: {valid}") from None
