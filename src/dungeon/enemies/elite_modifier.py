"""EliteModifier — transforma EnemyTemplate em versão Elite."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from random import Random

from src.core._paths import resolve_data_path
from src.core.characters.class_modifiers import ClassModifiers
from src.dungeon.enemies.enemy_template import EnemyTemplate

_BONUSES_FILE = "data/dungeon/enemies/elite_bonuses.json"
_ELITE_NAME_PREFIX = "Elite "

_SCALABLE_FIELDS = (
    "hit_dice",
    "mod_hp_flat",
    "mod_hp_mult",
    "mod_atk_physical",
    "mod_atk_magical",
    "mod_def_physical",
    "mod_def_magical",
)


@dataclass(frozen=True)
class EliteTierBonuses:
    """Bonus config para um tier de elite."""

    bonus_skill_pool: tuple[str, ...]
    bonus_count: int
    stat_scale_min: float
    stat_scale_max: float

    @classmethod
    def from_dict(cls, data: dict) -> EliteTierBonuses:
        return cls(
            bonus_skill_pool=tuple(data["bonus_skill_pool"]),
            bonus_count=int(data["bonus_count"]),
            stat_scale_min=float(data["stat_scale_min"]),
            stat_scale_max=float(data["stat_scale_max"]),
        )


def load_elite_bonuses() -> dict[int, EliteTierBonuses]:
    """Carrega bonuses de elite por tier."""
    path = resolve_data_path(_BONUSES_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {int(k): EliteTierBonuses.from_dict(v) for k, v in raw.items()}


def apply_elite(
    template: EnemyTemplate,
    bonuses: EliteTierBonuses,
    rng: Random | None = None,
) -> EnemyTemplate:
    """Retorna novo EnemyTemplate com stats escalados e skills bônus."""
    if rng is None:
        rng = Random()
    scale = _pick_scale(bonuses, rng)
    scaled_mods = _scale_modifiers(template.class_modifiers, scale)
    bonus_skills = _pick_bonus_skills(bonuses, rng)
    new_skill_ids = template.skill_ids + bonus_skills
    new_traits = template.special_traits + ("elite",)
    return EnemyTemplate(
        enemy_id=template.enemy_id,
        name=_ELITE_NAME_PREFIX + template.name,
        tier=template.tier,
        archetype=template.archetype,
        class_modifiers=scaled_mods,
        base_attributes=template.base_attributes,
        position=template.position,
        elemental_profile_id=template.elemental_profile_id,
        weapon_id=template.weapon_id,
        skill_ids=new_skill_ids,
        special_traits=new_traits,
    )


def _pick_scale(bonuses: EliteTierBonuses, rng: Random) -> float:
    return rng.uniform(bonuses.stat_scale_min, bonuses.stat_scale_max)


def _scale_modifiers(mods: ClassModifiers, scale: float) -> ClassModifiers:
    """Escala campos numéricos do ClassModifiers."""
    scaled = {}
    for field_name in _SCALABLE_FIELDS:
        original = getattr(mods, field_name)
        scaled[field_name] = math.ceil(original * scale)
    return ClassModifiers(
        **scaled,
        mana_multiplier=mods.mana_multiplier,
        regen_hp_mod=mods.regen_hp_mod,
        regen_mana_mod=mods.regen_mana_mod,
        preferred_attack_type=mods.preferred_attack_type,
    )


def _pick_bonus_skills(
    bonuses: EliteTierBonuses,
    rng: Random,
) -> tuple[str, ...]:
    """Sorteia bonus_count skills do pool sem repetição."""
    pool = list(bonuses.bonus_skill_pool)
    count = min(bonuses.bonus_count, len(pool))
    chosen = rng.sample(pool, count)
    return tuple(chosen)
