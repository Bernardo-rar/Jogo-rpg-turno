"""Testes para speed_indicator — ciclo de velocidade e opcoes."""

from src.ui.components.speed_indicator import (
    SPEED_OPTIONS,
    next_speed_index,
)


class TestSpeedOptions:
    def test_speed_options_has_three_values(self) -> None:
        assert len(SPEED_OPTIONS) == 3

    def test_speed_values(self) -> None:
        assert SPEED_OPTIONS == (1.0, 2.0, 3.0)


class TestNextSpeedIndex:
    def test_cycles_0_to_1(self) -> None:
        assert next_speed_index(0) == 1

    def test_cycles_1_to_2(self) -> None:
        assert next_speed_index(1) == 2

    def test_cycles_2_to_0(self) -> None:
        assert next_speed_index(2) == 0

    def test_next_speed_cycles_full_loop(self) -> None:
        idx = 0
        idx = next_speed_index(idx)
        assert idx == 1
        idx = next_speed_index(idx)
        assert idx == 2
        idx = next_speed_index(idx)
        assert idx == 0
