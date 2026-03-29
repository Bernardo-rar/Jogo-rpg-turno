"""XP reward config: XP base por tipo de encontro + bonus."""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.core._paths import resolve_data_path

_CONFIG_FILE = "data/progression/xp_rewards.json"


@dataclass(frozen=True)
class XpBonuses:
    """Multiplicadores bonus de XP."""

    no_death_mult: float
    fast_clear_max_rounds: int
    fast_clear_mult: float


@dataclass(frozen=True)
class XpRewardConfig:
    """Config completa de XP rewards."""

    normal_xp: dict[int, int]
    elite_xp: dict[int, int]
    boss_xp: dict[int, int]
    bonuses: XpBonuses

    def base_xp(self, encounter_type: str, tier: int) -> int:
        """Retorna XP base para tipo de encontro e tier."""
        tables = {
            "normal": self.normal_xp,
            "elite": self.elite_xp,
            "boss": self.boss_xp,
        }
        table = tables.get(encounter_type)
        if table is None:
            return 0
        return table.get(tier, 0)


def load_xp_reward_config() -> XpRewardConfig:
    """Carrega config de XP rewards do JSON."""
    path = resolve_data_path(_CONFIG_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _parse_config(raw)


def _parse_config(raw: dict) -> XpRewardConfig:
    enc = raw["encounter_xp"]
    bonuses = raw["bonuses"]
    return XpRewardConfig(
        normal_xp=_parse_tier_xp(enc["normal"]),
        elite_xp=_parse_tier_xp(enc["elite"]),
        boss_xp=_parse_tier_xp(enc["boss"]),
        bonuses=XpBonuses(
            no_death_mult=bonuses["no_death_mult"],
            fast_clear_max_rounds=bonuses["fast_clear_max_rounds"],
            fast_clear_mult=bonuses["fast_clear_mult"],
        ),
    )


def _parse_tier_xp(raw: dict[str, int]) -> dict[int, int]:
    return {int(k): v for k, v in raw.items()}
