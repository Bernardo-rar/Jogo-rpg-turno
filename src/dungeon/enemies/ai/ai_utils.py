"""Utilitarios compartilhados para IA de inimigos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.damage import DamageType, resolve_damage
from src.core.combat.targeting import AttackRange, get_valid_targets
from src.core.skills.skill import Skill
from src.core.skills.skill_effect_type import SkillEffectType

if TYPE_CHECKING:
    from src.core.characters.character import Character


def do_basic_attack(
    context: TurnContext,
    target: Character,
) -> list[CombatEvent]:
    """Executa ataque basico em alvo especifico."""
    from src.core.combat.basic_attack_resource import on_basic_attack

    if not context.action_economy.is_available(ActionType.ACTION):
        return []
    context.action_economy.use(ActionType.ACTION)
    atk_type = context.combatant.preferred_attack_type
    result = resolve_damage(
        attack_power=context.combatant.attack_power,
        defense=target.defense_for(atk_type),
    )
    target.take_damage(result.final_damage)
    on_basic_attack(context.combatant)
    return [
        CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=target.name,
            damage=result,
        ),
    ]


def get_usable_skills(context: TurnContext) -> list[Skill]:
    """Retorna skills prontas, com mana e action disponivel."""
    bar = context.combatant.skill_bar
    if bar is None:
        return []
    mana = context.combatant.current_mana
    economy = context.action_economy
    return [
        s for s in bar.ready_skills
        if s.mana_cost <= mana and economy.is_available(s.action_type)
    ]


def has_effect(skill: Skill, effect_type: SkillEffectType) -> bool:
    """Verifica se a skill tem ao menos um efeito do tipo dado."""
    return any(e.effect_type == effect_type for e in skill.effects)


def filter_by_effect(
    skills: list[Skill],
    effect_type: SkillEffectType,
) -> list[Skill]:
    """Filtra skills que contem ao menos um efeito do tipo."""
    return [s for s in skills if has_effect(s, effect_type)]


def get_valid_attack_targets(
    context: TurnContext,
) -> list[Character]:
    """Retorna alvos validos para ataque basico do combatente."""
    atk_type = context.combatant.preferred_attack_type
    attack_range = _range_for(atk_type)
    return get_valid_targets(attack_range, context.enemies)


def _range_for(damage_type: DamageType) -> AttackRange:
    if damage_type == DamageType.PHYSICAL:
        return AttackRange.MELEE
    return AttackRange.RANGED
