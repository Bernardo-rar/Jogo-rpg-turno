"""PhaseTransitionConfig — config de transicao one-shot entre fases de boss."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransitionEffect:
    """Um buff que o boss aplica em si mesmo ao entrar numa fase."""

    stat: str
    percent: float
    duration: int


@dataclass(frozen=True)
class PhaseTransitionConfig:
    """Config de transicao de fase: battle cry + self-buffs."""

    battle_cry: str = ""
    self_buffs: tuple[TransitionEffect, ...] = ()

    @classmethod
    def from_dict(cls, data: dict) -> PhaseTransitionConfig:
        """Constroi a partir de dict (JSON)."""
        buffs = tuple(
            TransitionEffect(
                stat=str(b["stat"]),
                percent=float(b["percent"]),
                duration=int(b["duration"]),
            )
            for b in data.get("self_buffs", ())
        )
        return cls(
            battle_cry=str(data.get("battle_cry", "")),
            self_buffs=buffs,
        )
