"""SkillHandler - TurnHandler que executa skills no combate."""

from __future__ import annotations

from src.core.combat.combat_engine import CombatEvent, EventType, TurnContext
from src.core.combat.skill_effect_applier import apply_skill_effect
from src.core.combat.target_resolver import resolve_targets
from src.core.skills.skill import Skill


class SkillHandler:
    """Seleciona e executa a primeira skill pronta com mana suficiente."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        skill = _pick_skill(context)
        if skill is None:
            return []
        return _execute_skill(skill, context)


def _pick_skill(context: TurnContext) -> Skill | None:
    """Retorna primeira skill pronta com mana e action disponivel."""
    bar = context.combatant.skill_bar
    if bar is None:
        return None
    economy = context.action_economy
    mana = context.combatant.current_mana
    for skill in bar.ready_skills:
        if skill.mana_cost <= mana and economy.is_available(skill.action_type):
            return skill
    return None


def _execute_skill(skill: Skill, context: TurnContext) -> list[CombatEvent]:
    """Consome recursos e aplica efeitos da skill."""
    context.action_economy.use(skill.action_type)
    context.combatant.spend_mana(skill.mana_cost)
    targets = resolve_targets(skill.target_type, context)
    events: list[CombatEvent] = []
    for effect in skill.effects:
        events.extend(apply_skill_effect(
            effect, targets, context.round_number,
            context.combatant,
        ))
    _start_cooldown(context, skill)
    return events


def _start_cooldown(context: TurnContext, skill: Skill) -> None:
    """Inicia cooldown da skill se aplicavel."""
    bar = context.combatant.skill_bar
    if bar is not None and skill.cooldown_turns > 0:
        bar.cooldown_tracker.start_cooldown(
            skill.skill_id, skill.cooldown_turns,
        )
