"""TankHandler - IA de archetype TANK: protege aliados, absorve dano."""

from __future__ import annotations

from src.core.characters.position import Position
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.skill_handler import execute_skill
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from src.dungeon.enemies.ai.ai_utils import (
    do_basic_attack,
    filter_by_effect,
    get_usable_skills,
    get_valid_attack_targets,
)


class TankHandler:
    """Buff/taunt turno 1 -> ataque front -> enrage se ultimo vivo."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        events: list[CombatEvent] = []
        if context.round_number == 1:
            buff_events = _try_opening_buff(context)
            if buff_events:
                return buff_events
        if _is_last_alive(context):
            events.extend(_try_enrage(context))
        events.extend(_attack_front(context))
        return events


def _try_opening_buff(context: TurnContext) -> list[CombatEvent]:
    """Usa buff/taunt no round 1."""
    skills = get_usable_skills(context)
    buffs = filter_by_effect(skills, SkillEffectType.BUFF)
    if not buffs:
        return []
    return execute_skill(buffs[0], context)


def _is_last_alive(context: TurnContext) -> bool:
    """Retorna True se nenhum aliado alem do combatente esta vivo."""
    return not any(
        a.is_alive
        for a in context.allies
        if a is not context.combatant
    )


def _try_enrage(context: TurnContext) -> list[CombatEvent]:
    """Usa self-buff se for o ultimo vivo."""
    skills = get_usable_skills(context)
    self_buffs = [
        s for s in skills
        if s.target_type == TargetType.SELF
        and SkillEffectType.BUFF in {e.effect_type for e in s.effects}
    ]
    if not self_buffs:
        return []
    return execute_skill(self_buffs[0], context)


def _attack_front(context: TurnContext) -> list[CombatEvent]:
    """Ataque basico no primeiro alvo front-line."""
    valid = get_valid_attack_targets(context)
    if not valid:
        return []
    front = [t for t in valid if t.position == Position.FRONT]
    target = front[0] if front else valid[0]
    return do_basic_attack(context, target)
