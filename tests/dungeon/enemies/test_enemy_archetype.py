"""Testes para EnemyArchetype enum."""

from src.dungeon.enemies.enemy_archetype import EnemyArchetype


class TestEnemyArchetype:

    def test_has_four_archetypes(self) -> None:
        assert len(EnemyArchetype) == 4

    def test_dps_value(self) -> None:
        assert EnemyArchetype.DPS.value == "dps"

    def test_tank_value(self) -> None:
        assert EnemyArchetype.TANK.value == "tank"

    def test_healer_value(self) -> None:
        assert EnemyArchetype.HEALER.value == "healer"

    def test_controller_value(self) -> None:
        assert EnemyArchetype.CONTROLLER.value == "controller"

    def test_from_string(self) -> None:
        assert EnemyArchetype("dps") is EnemyArchetype.DPS
