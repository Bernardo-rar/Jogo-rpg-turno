from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

GROOVE_CONFIG_DATA_PATH = "data/classes/bard_groove.json"


@dataclass(frozen=True)
class MusicalGrooveConfig:
    """Configuracao do Embalo Musical."""

    max_stacks: int
    gain_per_skill: int
    decay_per_turn: int
    buff_effectiveness_per_stack: float
    debuff_effectiveness_per_stack: float
    speed_bonus_per_stack: float
    crit_chance_per_stack: float
    crescendo_bonus: float
    crescendo_duration: int
    crescendo_reset_stacks: int


def load_groove_config(
    filepath: str = GROOVE_CONFIG_DATA_PATH,
) -> MusicalGrooveConfig:
    """Carrega configuracao do Embalo Musical do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return MusicalGrooveConfig(**data)


class MusicalGroove:
    """Embalo Musical: resource bar de stacks com crescendo."""

    def __init__(self, config: MusicalGrooveConfig) -> None:
        self._config = config
        self._stacks: int = 0
        self._crescendo_remaining: int = 0

    @property
    def stacks(self) -> int:
        return self._stacks

    @property
    def max_stacks(self) -> int:
        return self._config.max_stacks

    @property
    def is_crescendo(self) -> bool:
        return self._crescendo_remaining > 0

    def gain(self) -> None:
        """Ganha stacks ao usar skill."""
        self._stacks = min(
            self._stacks + self._config.gain_per_skill,
            self._config.max_stacks,
        )

    def decay(self) -> None:
        """Decai stacks por turno."""
        self._stacks = max(
            self._stacks - self._config.decay_per_turn, 0,
        )

    # --- Bonuses ---

    @property
    def buff_bonus(self) -> float:
        base = self._stacks * self._config.buff_effectiveness_per_stack
        if self.is_crescendo:
            return base + self._config.crescendo_bonus
        return base

    @property
    def debuff_bonus(self) -> float:
        base = self._stacks * self._config.debuff_effectiveness_per_stack
        if self.is_crescendo:
            return base + self._config.crescendo_bonus
        return base

    @property
    def speed_bonus(self) -> float:
        return self._stacks * self._config.speed_bonus_per_stack

    @property
    def crit_bonus(self) -> float:
        return self._stacks * self._config.crit_chance_per_stack

    # --- Crescendo ---

    def trigger_crescendo(self) -> bool:
        """Ativa crescendo se stacks no max. Retorna False se nao."""
        if self._stacks < self._config.max_stacks:
            return False
        self._crescendo_remaining = self._config.crescendo_duration
        return True

    def tick_crescendo(self) -> None:
        """Decrementa crescendo no fim do turno."""
        if self._crescendo_remaining <= 0:
            return
        self._crescendo_remaining -= 1
        if self._crescendo_remaining <= 0:
            self._stacks = self._config.crescendo_reset_stacks
