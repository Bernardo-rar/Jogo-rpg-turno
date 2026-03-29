"""Testes dos multiplicadores de posicao."""

from src.core.characters.position import Position
from src.core.combat.position_modifiers import (
    get_position_mod,
    scale_dealt,
    scale_taken,
)


class TestPositionModifiers:

    def test_front_dealt_boost(self) -> None:
        mod = get_position_mod(Position.FRONT)
        assert mod.damage_dealt_mult > 1.0

    def test_back_dealt_reduction(self) -> None:
        mod = get_position_mod(Position.BACK)
        assert mod.damage_dealt_mult < 1.0

    def test_front_taken_increase(self) -> None:
        mod = get_position_mod(Position.FRONT)
        assert mod.damage_taken_mult > 1.0

    def test_back_taken_decrease(self) -> None:
        mod = get_position_mod(Position.BACK)
        assert mod.damage_taken_mult < 1.0

    def test_scale_dealt_front_higher(self) -> None:
        front = scale_dealt(100, Position.FRONT)
        back = scale_dealt(100, Position.BACK)
        assert front > back

    def test_scale_taken_front_higher(self) -> None:
        front = scale_taken(100, Position.FRONT)
        back = scale_taken(100, Position.BACK)
        assert front > back

    def test_scale_dealt_values(self) -> None:
        assert scale_dealt(100, Position.FRONT) == 110
        assert scale_dealt(100, Position.BACK) == 90

    def test_scale_taken_values(self) -> None:
        front = scale_taken(100, Position.FRONT)
        back = scale_taken(100, Position.BACK)
        assert 114 <= front <= 115
        assert 84 <= back <= 85

    def test_minimum_1(self) -> None:
        assert scale_dealt(0, Position.BACK) == 1
        assert scale_taken(0, Position.BACK) == 1
