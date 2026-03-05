from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

MANA_ROTATION_DATA_PATH = "data/classes/sorcerer_mana_rotation.json"


@dataclass(frozen=True)
class ManaRotationConfig:
    """Configuracao da Rotacao de Mana do Sorcerer."""

    gain_ratio: float
    decay_per_turn: int
    max_ratio: float


def load_mana_rotation_config(
    filepath: str = MANA_ROTATION_DATA_PATH,
) -> ManaRotationConfig:
    """Carrega configuracao de rotacao de mana do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return ManaRotationConfig(**data)


class ManaRotation:
    """Barra de Rotacao de Mana do Sorcerer.

    Recurso que acumula ao causar dano magico.
    Mana armazenada e devolvida ao personagem.
    Decai por turno se nao causar dano.
    """

    def __init__(self, max_mana: int) -> None:
        self._current = 0
        self._max_mana = max_mana

    @property
    def current(self) -> int:
        return self._current

    @property
    def max_mana(self) -> int:
        return self._max_mana

    @property
    def ratio(self) -> float:
        """Razao de mana armazenada (0.0 a 1.0)."""
        if self._max_mana == 0:
            return 0.0
        return self._current / self._max_mana

    def gain(self, amount: int) -> int:
        """Ganha mana ate o maximo. Retorna quantidade real ganha."""
        actual = min(amount, self._max_mana - self._current)
        self._current += actual
        return actual

    def decay(self, amount: int) -> int:
        """Decai mana ate zero. Retorna quantidade real decaida."""
        actual = min(amount, self._current)
        self._current -= actual
        return actual

    def update_max(self, new_max: int) -> None:
        """Atualiza max mana. Clamp current se necessario."""
        self._max_mana = new_max
        self._current = min(self._current, self._max_mana)
