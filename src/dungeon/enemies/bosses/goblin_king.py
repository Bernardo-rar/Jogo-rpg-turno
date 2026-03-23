"""Goblin King — boss do Floor 1.

Phase 1 (>50% HP): War Cry buff aliados + ataque básico.
Phase 2 (<=50% HP): Enrage self-buff + Cleave AoE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.action_economy import ActionType
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
    from src.core.combat.combat_engine import CombatEvent, TurnContext

PHASE1_KEY = "goblin_king_p1"
PHASE2_KEY = "goblin_king_p2"


class GoblinKingPhase1:
    """Buff aliados com War Cry, depois ataque básico."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        events: list[CombatEvent] = []
        events.extend(_try_war_cry(context))
        events.extend(_try_attack(context))
        return events


class GoblinKingPhase2:
    """Enrage + Cleave AoE agressivo."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        events: list[CombatEvent] = []
        events.extend(_try_enrage(context))
        events.extend(_try_aoe_or_attack(context))
        return events


def _try_war_cry(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    buffs = filter_by_effect(skills, SkillEffectType.BUFF)
    bonus_buffs = [s for s in buffs if s.action_type == ActionType.BONUS_ACTION]
    if bonus_buffs:
        return execute_skill(bonus_buffs[0], context)
    return []


def _try_enrage(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    buffs = filter_by_effect(skills, SkillEffectType.BUFF)
    self_buffs = [
        s for s in buffs
        if s.action_type == ActionType.BONUS_ACTION
    ]
    if self_buffs:
        return execute_skill(self_buffs[0], context)
    return []


def _try_aoe_or_attack(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    aoe = filter_by_effect(skills, SkillEffectType.DAMAGE)
    action_aoe = [s for s in aoe if s.action_type == ActionType.ACTION]
    if action_aoe:
        return execute_skill(action_aoe[0], context)
    return _try_attack(context)


def _try_attack(context: TurnContext) -> list[CombatEvent]:
    targets = get_valid_attack_targets(context)
    target = pick_lowest_hp_ratio(targets)
    if target is None:
        return []
    return do_basic_attack(context, target)
