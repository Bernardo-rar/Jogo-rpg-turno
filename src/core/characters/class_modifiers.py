from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from src.core.combat.damage import DamageType


@dataclass(frozen=True)
class ClassModifiers:
    """Modificadores numericos especificos de cada classe."""

    hit_dice: int
    mod_hp_flat: int
    mod_hp_mult: int
    mana_multiplier: int
    mod_atk_physical: int
    mod_atk_magical: int
    mod_def_physical: int
    mod_def_magical: int
    regen_hp_mod: int
    regen_mana_mod: int
    preferred_attack_type: DamageType = DamageType.PHYSICAL

    @classmethod
    def from_dict(cls, data: dict) -> ClassModifiers:
        """Cria ClassModifiers a partir de um dict."""
        raw = dict(data)
        raw["preferred_attack_type"] = DamageType[
            raw.pop("preferred_attack_type", "PHYSICAL")
        ]
        return cls(**raw)

    @classmethod
    def from_json(cls, filepath: str) -> ClassModifiers:
        path = Path(filepath)
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(raw)
