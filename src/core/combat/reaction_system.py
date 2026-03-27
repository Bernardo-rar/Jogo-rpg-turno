"""Reaction system — enums e data types para reacoes de combate."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.core.combat.action_economy import ActionEconomy
    from src.core.combat.combat_engine import CombatEvent
    from src.core.characters.character import Character

from src.core.skills.skill import Skill


class ReactionTrigger(Enum):
    """Condicao que dispara uma reacao."""

    ON_DAMAGE_RECEIVED = "on_damage_received"
    ON_ALLY_DAMAGED = "on_ally_damaged"
    ON_ENEMY_ATTACK = "on_enemy_attack"
    ON_ENEMY_CAST = "on_enemy_cast"
    ON_COMBAT_START = "on_combat_start"
    ON_CRITICAL_HIT = "on_critical_hit"
    ON_ALLY_DEATH = "on_ally_death"
    ON_KILL = "on_kill"
    ON_LOW_HP = "on_low_hp"
    ON_ROUND_START = "on_round_start"


class ReactionMode(Enum):
    """Modo de ativacao da reacao."""

    PASSIVE = "passive"
    PREPARED = "prepared"
    TOGGLE = "toggle"


class ReactionHandler(Protocol):
    """Protocol para gerenciadores de reacao no combate."""

    def check_trigger(
        self,
        trigger: ReactionTrigger,
        target: Character,
        economy: ActionEconomy,
        round_number: int,
    ) -> list[CombatEvent]: ...


@dataclass(frozen=True)
class PreparedReaction:
    """Reacao preparada aguardando trigger."""

    skill: Skill
    combatant_name: str
    trigger: ReactionTrigger
