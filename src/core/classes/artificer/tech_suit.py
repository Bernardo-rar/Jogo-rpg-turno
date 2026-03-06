from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

SUIT_CONFIG_DATA_PATH = "data/classes/artificer_suit.json"


@dataclass(frozen=True)
class TechSuitConfig:
    """Configuracao do Traje Tecmagis."""

    atk_bonus_at_full: float
    phys_def_bonus_at_full: float
    mag_def_bonus_at_full: float


def load_suit_config(
    filepath: str = SUIT_CONFIG_DATA_PATH,
) -> TechSuitConfig:
    """Carrega configuracao do Traje Tecmagis do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return TechSuitConfig(**data)


class TechSuit:
    """Traje Tecmagis: stats escalam com mana ratio."""

    def __init__(self, config: TechSuitConfig) -> None:
        self._config = config

    @staticmethod
    def mana_ratio(current: int, maximum: int) -> float:
        """Calcula ratio de mana (0.0 a 1.0)."""
        if maximum <= 0:
            return 0.0
        return min(current / maximum, 1.0)

    def atk_multiplier(self, ratio: float) -> float:
        """Multiplicador de ataque magico baseado no mana ratio."""
        return 1.0 + ratio * self._config.atk_bonus_at_full

    def phys_def_multiplier(self, ratio: float) -> float:
        """Multiplicador de defesa fisica baseado no mana ratio."""
        return 1.0 + ratio * self._config.phys_def_bonus_at_full

    def mag_def_multiplier(self, ratio: float) -> float:
        """Multiplicador de defesa magica baseado no mana ratio."""
        return 1.0 + ratio * self._config.mag_def_bonus_at_full
