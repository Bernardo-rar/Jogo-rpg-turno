"""ReactionManager — gerencia reacoes preparadas e passivas no combate."""

from __future__ import annotations

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.reaction_system import (
    PreparedReaction,
    ReactionMode,
    ReactionTrigger,
)
from src.core.combat.skill_effect_applier import apply_skill_effect
from src.core.skills.class_resource_resolver import can_afford_all, spend_all
from src.core.skills.skill import Skill


class ReactionManager:
    """Gerencia reacoes preparadas e passivas."""

    def __init__(self) -> None:
        self._prepared: dict[str, PreparedReaction] = {}

    def prepare_reaction(
        self, combatant_name: str, skill: Skill,
    ) -> None:
        """Fila uma reacao preparada."""
        trigger = ReactionTrigger(skill.reaction_trigger)
        self._prepared[combatant_name] = PreparedReaction(
            skill=skill,
            combatant_name=combatant_name,
            trigger=trigger,
        )

    def has_prepared(self, combatant_name: str) -> bool:
        return combatant_name in self._prepared

    def clear_prepared(self, combatant_name: str) -> None:
        self._prepared.pop(combatant_name, None)

    def get_passive_reactions(self, combatant: object) -> list[Skill]:
        """Retorna reaction skills passivas do skill bar."""
        bar = getattr(combatant, "skill_bar", None)
        if bar is None:
            return []
        return [
            sk for sk in bar.all_skills
            if sk.reaction_mode == ReactionMode.PASSIVE.value
        ]

    def check_trigger(
        self,
        trigger: ReactionTrigger,
        target: object,
        economy: ActionEconomy,
        round_number: int,
    ) -> list[CombatEvent]:
        """Checa e dispara reacoes que casam com o trigger."""
        if not economy.is_available(ActionType.REACTION):
            return []
        skill = self._find_matching_reaction(trigger, target)
        if skill is None:
            return []
        if not can_afford_all(target, skill.resource_costs):
            return []
        return _fire_reaction(skill, target, economy, round_number)

    def _find_matching_reaction(
        self, trigger: ReactionTrigger, target: object,
    ) -> Skill | None:
        """Busca reacao passiva ou preparada que casa com trigger."""
        passive = self._find_passive(trigger, target)
        if passive is not None:
            return passive
        return self._find_prepared(trigger, target)

    def _find_passive(
        self, trigger: ReactionTrigger, target: object,
    ) -> Skill | None:
        for skill in self.get_passive_reactions(target):
            if skill.reaction_trigger == trigger.value:
                return skill
        return None

    def _find_prepared(
        self, trigger: ReactionTrigger, target: object,
    ) -> Skill | None:
        name = getattr(target, "name", "")
        prep = self._prepared.get(name)
        if prep is None:
            return None
        if prep.trigger != trigger:
            return None
        self._prepared.pop(name, None)
        return prep.skill


def _fire_reaction(
    skill: Skill,
    target: object,
    economy: ActionEconomy,
    round_number: int,
) -> list[CombatEvent]:
    """Dispara a reacao: consome REACTION + recursos + aplica efeitos."""
    economy.use(ActionType.REACTION)
    spend_all(target, skill.resource_costs)
    targets = [target]
    events: list[CombatEvent] = []
    for effect in skill.effects:
        events.extend(apply_skill_effect(
            effect, targets, round_number, target,
        ))
    return events
