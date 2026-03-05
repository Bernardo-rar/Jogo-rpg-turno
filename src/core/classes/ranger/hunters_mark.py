from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

MARK_DATA_PATH = "data/classes/ranger_mark.json"


@dataclass(frozen=True)
class HuntersMarkConfig:
    """Configuracao da Marca do Cacador."""

    armor_penetration_pct: float


def load_hunters_mark_config(
    filepath: str = MARK_DATA_PATH,
) -> HuntersMarkConfig:
    """Carrega configuracao de marca do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return HuntersMarkConfig(**data)


class HuntersMark:
    """Marca do Cacador: rastreia alvo marcado pelo Ranger."""

    def __init__(self) -> None:
        self._target_name: str | None = None

    @property
    def target_name(self) -> str | None:
        return self._target_name

    @property
    def is_active(self) -> bool:
        return self._target_name is not None

    def mark(self, target_name: str) -> None:
        """Marca um alvo. Substitui marca anterior."""
        self._target_name = target_name

    def clear(self) -> None:
        """Remove marca ativa."""
        self._target_name = None
