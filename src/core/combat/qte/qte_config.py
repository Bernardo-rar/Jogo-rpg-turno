"""QTE config — data models for Quick Time Events."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

DEFAULT_TIME_WINDOW_MS = 2500
DEFAULT_DIFFICULTY = "MEDIUM"

PERFECT_MULT = 1.30
PARTIAL_MULT = 1.15
FAILURE_MULT = 0.90
SKIPPED_MULT = 1.00
PARTIAL_THRESHOLD = 0.50


class QteOutcome(Enum):
    """Result of a QTE attempt."""

    PERFECT = auto()
    PARTIAL = auto()
    FAILURE = auto()
    SKIPPED = auto()


@dataclass(frozen=True)
class QteSequence:
    """QTE configuration attached to a skill."""

    keys: tuple[str, ...]
    time_window_ms: int = DEFAULT_TIME_WINDOW_MS
    difficulty: str = DEFAULT_DIFFICULTY

    @classmethod
    def from_dict(cls, data: dict) -> QteSequence:
        return cls(
            keys=tuple(data["keys"]),
            time_window_ms=int(
                data.get("time_window_ms", DEFAULT_TIME_WINDOW_MS),
            ),
            difficulty=str(data.get("difficulty", DEFAULT_DIFFICULTY)),
        )


@dataclass(frozen=True)
class QteResult:
    """Outcome of a QTE evaluation."""

    outcome: QteOutcome
    correct_count: int
    total_count: int
    multiplier: float
