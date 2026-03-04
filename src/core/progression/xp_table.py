"""XP table: thresholds de XP necessario para cada nivel."""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.core._paths import resolve_data_path

MIN_LEVEL = 1


@dataclass(frozen=True)
class XpTable:
    """Tabela imutavel de thresholds de XP por nivel.

    thresholds[0] = XP para level 1 (sempre 0),
    thresholds[1] = XP para level 2, etc.
    """

    thresholds: tuple[int, ...]

    @property
    def max_level(self) -> int:
        return len(self.thresholds)

    def threshold_for_level(self, level: int) -> int:
        """Retorna XP necessario para alcancar o nivel dado."""
        if level < MIN_LEVEL or level > self.max_level:
            msg = f"Level {level} fora do range [{MIN_LEVEL}, {self.max_level}]"
            raise ValueError(msg)
        return self.thresholds[level - 1]


def level_for_xp(xp: int, table: XpTable) -> int:
    """Retorna o nivel correspondente ao total de XP acumulado."""
    current_level = MIN_LEVEL
    for i, threshold in enumerate(table.thresholds):
        if xp >= threshold:
            current_level = i + 1
    return current_level


def load_xp_table() -> XpTable:
    """Carrega XP table do JSON em data/progression/xp_table.json."""
    path = resolve_data_path("data/progression/xp_table.json")
    with open(path) as f:
        raw = json.load(f)
    return XpTable(thresholds=tuple(raw["xp_thresholds"]))
