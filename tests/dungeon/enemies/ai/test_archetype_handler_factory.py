"""Testes para archetype_handler_factory."""

from __future__ import annotations

import pytest

from src.dungeon.enemies.ai.archetype_handler_factory import create_handler
from src.dungeon.enemies.ai.controller_handler import ControllerHandler
from src.dungeon.enemies.ai.dps_handler import DpsHandler
from src.dungeon.enemies.ai.healer_handler import HealerHandler
from src.dungeon.enemies.ai.tank_handler import TankHandler
from src.dungeon.enemies.enemy_archetype import EnemyArchetype


class TestCreateHandler:

    def test_dps_returns_dps_handler(self) -> None:
        handler = create_handler(EnemyArchetype.DPS)
        assert isinstance(handler, DpsHandler)

    def test_tank_returns_tank_handler(self) -> None:
        handler = create_handler(EnemyArchetype.TANK)
        assert isinstance(handler, TankHandler)

    def test_healer_returns_healer_handler(self) -> None:
        handler = create_handler(EnemyArchetype.HEALER)
        assert isinstance(handler, HealerHandler)

    def test_controller_returns_controller_handler(self) -> None:
        handler = create_handler(EnemyArchetype.CONTROLLER)
        assert isinstance(handler, ControllerHandler)

    def test_all_archetypes_have_handlers(self) -> None:
        for archetype in EnemyArchetype:
            handler = create_handler(archetype)
            assert hasattr(handler, "execute_turn")
