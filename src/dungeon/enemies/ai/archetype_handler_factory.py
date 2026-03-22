"""Factory que mapeia EnemyArchetype para TurnHandler."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.dungeon.enemies.ai.controller_handler import ControllerHandler
from src.dungeon.enemies.ai.dps_handler import DpsHandler
from src.dungeon.enemies.ai.healer_handler import HealerHandler
from src.dungeon.enemies.ai.tank_handler import TankHandler
from src.dungeon.enemies.enemy_archetype import EnemyArchetype

if TYPE_CHECKING:
    from src.core.combat.combat_engine import TurnHandler

_HANDLER_MAP: dict[EnemyArchetype, type] = {
    EnemyArchetype.DPS: DpsHandler,
    EnemyArchetype.TANK: TankHandler,
    EnemyArchetype.HEALER: HealerHandler,
    EnemyArchetype.CONTROLLER: ControllerHandler,
}


def create_handler(archetype: EnemyArchetype) -> TurnHandler:
    """Cria TurnHandler apropriado para o archetype."""
    handler_cls = _HANDLER_MAP[archetype]
    return handler_cls()
