"""PassiveManager — dispara passive skills automaticamente em resposta a eventos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent
from src.core.combat.skill_effect_applier import apply_skill_effect

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.skills.skill import Skill

LOW_HP_THRESHOLD = 0.5


class PassiveManager:
    """Dispara passive skills automaticamente em resposta a eventos."""

    def fire_on_round_start(
        self, combatants: list[Character], round_number: int,
    ) -> list[CombatEvent]:
        """Fires ON_ROUND_START passives for all combatants."""
        events: list[CombatEvent] = []
        for combatant in combatants:
            matching = _get_passive_skills(combatant, "on_round_start")
            events.extend(
                _fire_passives(matching, combatant, round_number),
            )
        return events

    def fire_on_kill(
        self, killer: Character, round_number: int,
    ) -> list[CombatEvent]:
        """Fires ON_KILL passives for the killer."""
        matching = _get_passive_skills(killer, "on_kill")
        return _fire_passives(matching, killer, round_number)

    def fire_on_critical(
        self, attacker: Character, round_number: int,
    ) -> list[CombatEvent]:
        """Fires ON_CRITICAL_HIT passives for the attacker."""
        matching = _get_passive_skills(attacker, "on_critical_hit")
        return _fire_passives(matching, attacker, round_number)

    def fire_on_low_hp(
        self, target: Character, round_number: int,
    ) -> list[CombatEvent]:
        """Fires ON_LOW_HP passives when target HP <= 50%."""
        if not _is_below_hp_threshold(target):
            return []
        matching = _get_passive_skills(target, "on_low_hp")
        return _fire_passives(matching, target, round_number)

    def fire_on_ally_death(
        self, dead_ally_name: str, party: list[Character],
        round_number: int,
    ) -> list[CombatEvent]:
        """Fires ON_ALLY_DEATH passives for surviving party members."""
        events: list[CombatEvent] = []
        for member in party:
            matching = _get_passive_skills(member, "on_ally_death")
            events.extend(
                _fire_passives(matching, member, round_number),
            )
        return events


def _is_below_hp_threshold(target: Character) -> bool:
    if target.max_hp == 0:
        return False
    return target.current_hp / target.max_hp <= LOW_HP_THRESHOLD


def _get_passive_skills(
    combatant: Character, trigger: str,
) -> list[Skill]:
    """Filtra skills passivas do combatant que correspondem ao trigger."""
    skill_bar = combatant.skill_bar
    if skill_bar is None:
        return []
    return [
        sk for sk in skill_bar.all_skills
        if sk.action_type == ActionType.PASSIVE
        and sk.reaction_trigger == trigger
    ]


def _fire_passives(
    skills: list[Skill], combatant: Character, round_number: int,
) -> list[CombatEvent]:
    """Aplica efeitos de cada skill passiva ao proprio combatant."""
    events: list[CombatEvent] = []
    for skill in skills:
        for effect in skill.effects:
            events.extend(
                apply_skill_effect(
                    effect, [combatant], round_number, combatant,
                ),
            )
    return events
