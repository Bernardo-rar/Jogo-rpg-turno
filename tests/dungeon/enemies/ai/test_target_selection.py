"""Testes para funcoes puras de selecao de alvo."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.characters.position import Position
from src.dungeon.enemies.ai.target_selection import (
    pick_backline_targets,
    pick_highest_threat,
    pick_lowest_hp_ratio,
)


@dataclass
class _FakeTarget:
    """Stub minimo para testes de targeting."""

    name: str
    current_hp: int
    max_hp: int
    position: Position
    attack_power: int
    is_alive: bool = True


class TestPickLowestHpRatio:

    def test_returns_most_injured(self) -> None:
        targets = [
            _FakeTarget("A", 80, 100, Position.FRONT, 10),
            _FakeTarget("B", 30, 100, Position.FRONT, 10),
            _FakeTarget("C", 60, 100, Position.BACK, 10),
        ]
        result = pick_lowest_hp_ratio(targets)
        assert result is not None
        assert result.name == "B"

    def test_ignores_dead(self) -> None:
        targets = [
            _FakeTarget("Dead", 0, 100, Position.FRONT, 10, is_alive=False),
            _FakeTarget("Alive", 50, 100, Position.FRONT, 10),
        ]
        result = pick_lowest_hp_ratio(targets)
        assert result is not None
        assert result.name == "Alive"

    def test_returns_none_if_all_dead(self) -> None:
        targets = [
            _FakeTarget("X", 0, 100, Position.FRONT, 10, is_alive=False),
        ]
        assert pick_lowest_hp_ratio(targets) is None

    def test_returns_none_for_empty_list(self) -> None:
        assert pick_lowest_hp_ratio([]) is None

    def test_handles_zero_max_hp(self) -> None:
        targets = [
            _FakeTarget("Zero", 0, 0, Position.FRONT, 10),
            _FakeTarget("Normal", 50, 100, Position.FRONT, 10),
        ]
        result = pick_lowest_hp_ratio(targets)
        assert result is not None
        assert result.name == "Normal"


class TestPickBacklineTargets:

    def test_filters_back_position(self) -> None:
        targets = [
            _FakeTarget("Front", 100, 100, Position.FRONT, 10),
            _FakeTarget("Back1", 100, 100, Position.BACK, 10),
            _FakeTarget("Back2", 100, 100, Position.BACK, 10),
        ]
        result = pick_backline_targets(targets)
        assert len(result) == 2
        assert all(t.position == Position.BACK for t in result)

    def test_ignores_dead(self) -> None:
        targets = [
            _FakeTarget("Dead", 0, 100, Position.BACK, 10, is_alive=False),
            _FakeTarget("Alive", 100, 100, Position.BACK, 10),
        ]
        result = pick_backline_targets(targets)
        assert len(result) == 1
        assert result[0].name == "Alive"

    def test_returns_empty_if_no_back(self) -> None:
        targets = [
            _FakeTarget("Front", 100, 100, Position.FRONT, 10),
        ]
        assert pick_backline_targets(targets) == []


class TestPickHighestThreat:

    def test_returns_highest_attack_power(self) -> None:
        targets = [
            _FakeTarget("Weak", 100, 100, Position.FRONT, 5),
            _FakeTarget("Strong", 100, 100, Position.FRONT, 20),
            _FakeTarget("Medium", 100, 100, Position.BACK, 12),
        ]
        result = pick_highest_threat(targets)
        assert result is not None
        assert result.name == "Strong"

    def test_ignores_dead(self) -> None:
        targets = [
            _FakeTarget("Dead", 0, 100, Position.FRONT, 99, is_alive=False),
            _FakeTarget("Alive", 100, 100, Position.FRONT, 5),
        ]
        result = pick_highest_threat(targets)
        assert result is not None
        assert result.name == "Alive"

    def test_returns_none_for_empty_list(self) -> None:
        assert pick_highest_threat([]) is None
