"""Reaction system — enums e data types para reacoes de combate."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.core.skills.skill import Skill


class ReactionTrigger(Enum):
    """Condicao que dispara uma reacao."""

    ON_DAMAGE_RECEIVED = "on_damage_received"
    ON_ALLY_DAMAGED = "on_ally_damaged"
    ON_ENEMY_ATTACK = "on_enemy_attack"
    ON_ENEMY_CAST = "on_enemy_cast"


class ReactionMode(Enum):
    """Modo de ativacao da reacao."""

    PASSIVE = "passive"
    PREPARED = "prepared"
    TOGGLE = "toggle"


@dataclass(frozen=True)
class PreparedReaction:
    """Reacao preparada aguardando trigger."""

    skill: Skill
    combatant_name: str
    trigger: ReactionTrigger
