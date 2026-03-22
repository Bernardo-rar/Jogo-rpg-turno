"""HealerHandler - IA de archetype HEALER: prioriza cura de aliados."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.skill_handler import execute_skill
from src.core.skills.skill_effect_type import SkillEffectType
from src.dungeon.enemies.ai.ai_utils import (
    do_basic_attack,
    filter_by_effect,
    get_usable_skills,
    get_valid_attack_targets,
)
from src.dungeon.enemies.ai.target_selection import pick_lowest_hp_ratio

if TYPE_CHECKING:
    from src.core.characters.character import Character

_HEAL_THRESHOLD = 0.6
_HEALTHY_THRESHOLD = 0.8


class HealerHandler:
    """Heal ally <60% HP -> buff se todos >80% -> basic attack."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        heal_events = _try_heal(context)
        if heal_events:
            return heal_events
        buff_events = _try_buff_if_healthy(context)
        if buff_events:
            return buff_events
        return _fallback_attack(context)


def _try_heal(context: TurnContext) -> list[CombatEvent]:
    """Cura aliado com HP abaixo do threshold."""
    hurt = _find_hurt_ally(context)
    if hurt is None:
        return []
    skills = get_usable_skills(context)
    heals = filter_by_effect(skills, SkillEffectType.HEAL)
    if not heals:
        return []
    return execute_skill(heals[0], context)


def _find_hurt_ally(context: TurnContext) -> Character | None:
    """Retorna aliado vivo com HP ratio abaixo de _HEAL_THRESHOLD."""
    alive = [a for a in context.allies if a.is_alive]
    for ally in alive:
        ratio = ally.current_hp / max(ally.max_hp, 1)
        if ratio < _HEAL_THRESHOLD:
            return ally
    return None


def _try_buff_if_healthy(context: TurnContext) -> list[CombatEvent]:
    """Usa buff se todos os aliados estao acima de _HEALTHY_THRESHOLD."""
    if not _all_allies_above(context, _HEALTHY_THRESHOLD):
        return []
    skills = get_usable_skills(context)
    buffs = filter_by_effect(skills, SkillEffectType.BUFF)
    if not buffs:
        return []
    return execute_skill(buffs[0], context)


def _all_allies_above(ctx: TurnContext, threshold: float) -> bool:
    alive = [a for a in ctx.allies if a.is_alive]
    return all(
        a.current_hp / max(a.max_hp, 1) >= threshold for a in alive
    )


def _fallback_attack(context: TurnContext) -> list[CombatEvent]:
    """Ataque basico no inimigo mais fraco."""
    valid = get_valid_attack_targets(context)
    target = pick_lowest_hp_ratio(valid) if valid else None
    if target is None:
        return []
    return do_basic_attack(context, target)
