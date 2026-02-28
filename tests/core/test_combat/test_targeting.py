import pytest

from src.core.characters.position import Position
from src.core.combat.targeting import AttackRange, get_valid_targets


class FakeTargetable:
    """Fake que implementa Targetable Protocol para testes."""

    def __init__(
        self, name: str, position: Position, alive: bool = True
    ) -> None:
        self._name = name
        self._position = position
        self._alive = alive

    @property
    def name(self) -> str:
        return self._name

    @property
    def position(self) -> Position:
        return self._position

    @property
    def is_alive(self) -> bool:
        return self._alive


class TestAttackRange:
    def test_has_melee(self):
        assert AttackRange.MELEE is not None

    def test_has_ranged(self):
        assert AttackRange.RANGED is not None

    def test_has_two_values(self):
        assert len(list(AttackRange)) == 2


class TestMeleeTargeting:
    def test_melee_returns_only_front_enemies(self):
        front = FakeTargetable("F", Position.FRONT)
        back = FakeTargetable("B", Position.BACK)
        result = get_valid_targets(AttackRange.MELEE, [front, back])
        assert result == [front]

    def test_melee_fallback_to_back_when_no_front_alive(self):
        dead_front = FakeTargetable("F", Position.FRONT, alive=False)
        back = FakeTargetable("B", Position.BACK)
        result = get_valid_targets(AttackRange.MELEE, [dead_front, back])
        assert result == [back]

    def test_melee_excludes_dead_from_front(self):
        alive_front = FakeTargetable("A", Position.FRONT)
        dead_front = FakeTargetable("D", Position.FRONT, alive=False)
        result = get_valid_targets(AttackRange.MELEE, [alive_front, dead_front])
        assert result == [alive_front]

    def test_melee_multiple_front_returns_all_alive_front(self):
        f1 = FakeTargetable("F1", Position.FRONT)
        f2 = FakeTargetable("F2", Position.FRONT)
        back = FakeTargetable("B", Position.BACK)
        result = get_valid_targets(AttackRange.MELEE, [f1, f2, back])
        assert result == [f1, f2]

    def test_melee_all_front_dead_returns_all_alive_back(self):
        dead1 = FakeTargetable("D1", Position.FRONT, alive=False)
        dead2 = FakeTargetable("D2", Position.FRONT, alive=False)
        b1 = FakeTargetable("B1", Position.BACK)
        b2 = FakeTargetable("B2", Position.BACK)
        result = get_valid_targets(AttackRange.MELEE, [dead1, dead2, b1, b2])
        assert result == [b1, b2]


class TestRangedTargeting:
    def test_ranged_returns_all_alive_regardless_of_position(self):
        front = FakeTargetable("F", Position.FRONT)
        back = FakeTargetable("B", Position.BACK)
        result = get_valid_targets(AttackRange.RANGED, [front, back])
        assert result == [front, back]

    def test_ranged_excludes_dead(self):
        alive = FakeTargetable("A", Position.FRONT)
        dead = FakeTargetable("D", Position.BACK, alive=False)
        result = get_valid_targets(AttackRange.RANGED, [alive, dead])
        assert result == [alive]

    def test_ranged_returns_only_back_if_front_dead(self):
        dead_front = FakeTargetable("F", Position.FRONT, alive=False)
        back = FakeTargetable("B", Position.BACK)
        result = get_valid_targets(AttackRange.RANGED, [dead_front, back])
        assert result == [back]


class TestTargetingEdgeCases:
    def test_empty_enemies_returns_empty(self):
        result = get_valid_targets(AttackRange.MELEE, [])
        assert result == []

    def test_all_dead_returns_empty(self):
        d1 = FakeTargetable("D1", Position.FRONT, alive=False)
        d2 = FakeTargetable("D2", Position.BACK, alive=False)
        assert get_valid_targets(AttackRange.MELEE, [d1, d2]) == []
        assert get_valid_targets(AttackRange.RANGED, [d1, d2]) == []

    def test_single_front_enemy_melee(self):
        enemy = FakeTargetable("E", Position.FRONT)
        result = get_valid_targets(AttackRange.MELEE, [enemy])
        assert result == [enemy]

    def test_single_back_enemy_melee_fallback(self):
        enemy = FakeTargetable("E", Position.BACK)
        result = get_valid_targets(AttackRange.MELEE, [enemy])
        assert result == [enemy]
