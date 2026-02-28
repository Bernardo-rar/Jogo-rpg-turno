from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClassModifiers:
    """Modificadores numericos especificos de cada classe."""

    hit_dice: int
    vida_mod: int
    mod_hp: int
    mana_multiplier: int
    mod_atk_physical: int
    mod_atk_magical: int
    mod_def_physical: int
    mod_def_magical: int
    regen_hp_mod: int
    regen_mana_mod: int

    @classmethod
    def from_json(cls, filepath: str) -> ClassModifiers:
        path = Path(filepath)
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(**raw)
