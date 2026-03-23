"""BossPhase — define fases de boss por HP threshold."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BossPhase:
    """Uma fase de boss, ativa enquanto HP ratio > threshold."""

    phase_number: int
    hp_threshold: float
    handler_key: str

    @classmethod
    def from_dict(cls, data: dict) -> BossPhase:
        return cls(
            phase_number=int(data["phase_number"]),
            hp_threshold=float(data["hp_threshold"]),
            handler_key=str(data["handler_key"]),
        )
