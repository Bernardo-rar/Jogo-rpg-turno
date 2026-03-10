"""Resolve TargetType em lista concreta de alvos a partir do TurnContext."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.characters.position import Position
from src.core.skills.target_type import TargetType

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.combat.combat_engine import TurnContext


def resolve_targets(
    target_type: TargetType, context: TurnContext,
) -> list[Character]:
    """Mapeia TargetType para lista de alvos concretos."""
    resolver = _RESOLVERS[target_type]
    return resolver(context)


def _resolve_self(context: TurnContext) -> list[Character]:
    return [context.combatant]


def _resolve_single_ally(context: TurnContext) -> list[Character]:
    alive = [a for a in context.allies if a.is_alive]
    if not alive:
        return []
    most_hurt = min(alive, key=_hp_ratio)
    return [most_hurt]


def _hp_ratio(char: Character) -> float:
    if char.max_hp == 0:
        return 1.0
    return char.current_hp / char.max_hp


def _resolve_single_enemy(context: TurnContext) -> list[Character]:
    alive = [e for e in context.enemies if e.is_alive]
    front = [e for e in alive if e.position == Position.FRONT]
    targets = front if front else alive
    return targets[:1]


def _resolve_all_allies(context: TurnContext) -> list[Character]:
    return [a for a in context.allies if a.is_alive]


def _resolve_all_enemies(context: TurnContext) -> list[Character]:
    return [e for e in context.enemies if e.is_alive]


_RESOLVERS = {
    TargetType.SELF: _resolve_self,
    TargetType.SINGLE_ALLY: _resolve_single_ally,
    TargetType.SINGLE_ENEMY: _resolve_single_enemy,
    TargetType.ALL_ALLIES: _resolve_all_allies,
    TargetType.ALL_ENEMIES: _resolve_all_enemies,
}
