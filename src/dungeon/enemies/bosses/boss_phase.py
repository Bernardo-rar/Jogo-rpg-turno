"""BossPhase — define fases de boss por HP threshold."""

from __future__ import annotations

from dataclasses import dataclass

from src.dungeon.enemies.bosses.phase_transition import PhaseTransitionConfig


@dataclass(frozen=True)
class BossPhase:
    """Uma fase de boss, ativa enquanto HP ratio > threshold."""

    phase_number: int
    hp_threshold: float
    handler_key: str
    transition: PhaseTransitionConfig | None = None

    @classmethod
    def from_dict(cls, data: dict) -> BossPhase:
        """Constroi a partir de dict (JSON)."""
        raw_transition = data.get("transition")
        transition = (
            PhaseTransitionConfig.from_dict(raw_transition)
            if raw_transition is not None
            else None
        )
        return cls(
            phase_number=int(data["phase_number"]),
            hp_threshold=float(data["hp_threshold"]),
            handler_key=str(data["handler_key"]),
            transition=transition,
        )
