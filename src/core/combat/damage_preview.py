"""Previsao de dano/cura para o tooltip de combate. Funcoes puras."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core.combat.damage import (
    BASE_CRIT_CHANCE,
    DEFAULT_CRIT_MULTIPLIER,
    MIN_DAMAGE,
    DamageType,
    calculate_crit_chance,
)
from src.core.skills.skill_effect_type import SkillEffectType

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.elements.element_type import ElementType
    from src.core.skills.skill import Skill


@dataclass(frozen=True)
class AttackPreview:
    """Previsao de um ataque basico."""

    min_damage: int
    max_damage: int
    crit_chance_pct: float
    damage_type: DamageType


@dataclass(frozen=True)
class SkillDamagePreview:
    """Previsao de dano de uma skill."""

    min_damage: int
    max_damage: int
    crit_chance_pct: float
    damage_type: DamageType
    element: ElementType | None
    mana_cost: int
    skill_name: str


@dataclass(frozen=True)
class HealPreview:
    """Previsao de cura de uma skill."""

    estimated_heal: int
    mana_cost: int
    skill_name: str
    target_hp_current: int
    target_hp_max: int


def preview_basic_attack(
    attacker: Character, target: Character,
) -> AttackPreview:
    """Calcula preview de ataque basico sem randomizar crit."""
    attack = attacker.physical_attack
    defense = target.physical_defense
    normal = max(MIN_DAMAGE, attack - defense)
    crit = max(MIN_DAMAGE, attack * DEFAULT_CRIT_MULTIPLIER - defense)
    crit_chance = calculate_crit_chance(0)
    return AttackPreview(
        min_damage=normal,
        max_damage=crit,
        crit_chance_pct=round(crit_chance * 100, 1),
        damage_type=DamageType.PHYSICAL,
    )


def preview_skill_damage(
    skill: Skill, attacker: Character, target: Character,
) -> SkillDamagePreview | None:
    """Calcula preview de dano da primeira skill effect DAMAGE."""
    dmg_effect = _find_damage_effect(skill)
    if dmg_effect is None:
        return None
    is_magical = dmg_effect.element is not None
    base_power = dmg_effect.base_power
    if is_magical:
        attack = base_power + attacker.magical_attack
        defense = target.magical_defense
        dtype = DamageType.MAGICAL
    else:
        attack = base_power + attacker.physical_attack
        defense = target.physical_defense
        dtype = DamageType.PHYSICAL
    normal = max(MIN_DAMAGE, attack - defense)
    crit = max(MIN_DAMAGE, attack * DEFAULT_CRIT_MULTIPLIER - defense)
    crit_chance = calculate_crit_chance(0)
    return SkillDamagePreview(
        min_damage=normal,
        max_damage=crit,
        crit_chance_pct=round(crit_chance * 100, 1),
        damage_type=dtype,
        element=dmg_effect.element,
        mana_cost=skill.mana_cost,
        skill_name=skill.name,
    )


def preview_heal(
    skill: Skill, caster: Character, target: Character,
) -> HealPreview | None:
    """Calcula preview de cura da primeira skill effect HEAL."""
    heal_effect = _find_heal_effect(skill)
    if heal_effect is None:
        return None
    heal_power = heal_effect.base_power + caster.magical_attack
    missing = target.max_hp - target.current_hp
    estimated = min(heal_power, missing)
    return HealPreview(
        estimated_heal=estimated,
        mana_cost=skill.mana_cost,
        skill_name=skill.name,
        target_hp_current=target.current_hp,
        target_hp_max=target.max_hp,
    )


def _find_damage_effect(skill: Skill) -> object | None:
    for eff in skill.effects:
        if eff.effect_type == SkillEffectType.DAMAGE:
            return eff
    return None


def _find_heal_effect(skill: Skill) -> object | None:
    for eff in skill.effects:
        if eff.effect_type == SkillEffectType.HEAL:
            return eff
    return None
