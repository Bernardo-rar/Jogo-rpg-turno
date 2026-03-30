"""PassiveEventDispatcher — fires passive triggers from combat events."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.combat.combat_engine import CombatEvent
    from src.core.combat.passive_manager import PassiveManager


class PassiveEventDispatcher:
    """Dispatches passive skill triggers based on combat events."""

    def __init__(
        self,
        passive_manager: PassiveManager,
        participants: dict[str, Character],
        party: list[Character],
        enemies: list[Character],
    ) -> None:
        self._pm = passive_manager
        self._participants = participants
        self._party = party
        self._enemies = enemies

    def fire_round_start(self, round_number: int) -> list[CombatEvent]:
        """Fires on_round_start passives for all alive combatants."""
        alive = [c for c in self._participants.values() if c.is_alive]
        return self._pm.fire_on_round_start(alive, round_number)

    def fire_event_passives(
        self, events: list[CombatEvent], round_number: int,
    ) -> list[CombatEvent]:
        """Fires kill, low_hp, and critical passives from events."""
        result: list[CombatEvent] = []
        result.extend(self._fire_kill_passives(events, round_number))
        result.extend(self._fire_damage_passives(events, round_number))
        return result

    def _fire_kill_passives(
        self, events: list[CombatEvent], round_number: int,
    ) -> list[CombatEvent]:
        """Detects deaths and fires on_kill + on_ally_death."""
        fired: set[str] = set()
        result: list[CombatEvent] = []
        for event in events:
            target = self._participants.get(event.target_name)
            if target is None or target.is_alive:
                continue
            if event.target_name in fired:
                continue
            fired.add(event.target_name)
            result.extend(
                self._fire_single_kill(event, round_number),
            )
        return result

    def _fire_single_kill(
        self, event: CombatEvent, round_number: int,
    ) -> list[CombatEvent]:
        """Fires on_kill for actor and on_ally_death for the team."""
        result: list[CombatEvent] = []
        actor = self._participants.get(event.actor_name)
        if actor is not None and actor.is_alive:
            result.extend(self._pm.fire_on_kill(actor, round_number))
        dead_char = self._participants.get(event.target_name)
        if dead_char is not None:
            result.extend(
                self._fire_ally_death(dead_char, round_number),
            )
        return result

    def _fire_ally_death(
        self, dead_char: Character, round_number: int,
    ) -> list[CombatEvent]:
        """Fires on_ally_death for the dead character's team."""
        _, allies = _get_teams(dead_char, self._party, self._enemies)
        team = [dead_char] + allies
        survivors = [c for c in team if c.is_alive]
        return self._pm.fire_on_ally_death(
            dead_char.name, survivors, round_number,
        )

    def _fire_damage_passives(
        self, events: list[CombatEvent], round_number: int,
    ) -> list[CombatEvent]:
        """Fires on_low_hp and on_critical for damage events."""
        result: list[CombatEvent] = []
        for event in events:
            if event.damage is None:
                continue
            result.extend(
                self._fire_low_hp_and_crit(event, round_number),
            )
        return result

    def _fire_low_hp_and_crit(
        self, event: CombatEvent, round_number: int,
    ) -> list[CombatEvent]:
        """Fires on_low_hp for target and on_critical for actor."""
        result: list[CombatEvent] = []
        target = self._participants.get(event.target_name)
        if target is not None and target.is_alive:
            result.extend(
                self._pm.fire_on_low_hp(target, round_number),
            )
        if event.damage and event.damage.is_critical:
            actor = self._participants.get(event.actor_name)
            if actor is not None and actor.is_alive:
                result.extend(
                    self._pm.fire_on_critical(actor, round_number),
                )
        return result


def _get_teams(
    combatant: Character,
    party: list[Character],
    enemies: list[Character],
) -> tuple[list[Character], list[Character]]:
    """Returns (own_team, opponent_team) for the combatant."""
    if combatant in party:
        return party, enemies
    return enemies, party
