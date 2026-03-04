"""Testes para LevelUpResult frozen dataclass."""

import pytest

from src.core.progression.level_up_result import LevelUpResult


class TestLevelUpResult:
    def test_creates_with_values(self) -> None:
        result = LevelUpResult(new_level=2, physical_points=2, mental_points=1)
        assert result.new_level == 2
        assert result.physical_points == 2
        assert result.mental_points == 1

    def test_is_frozen(self) -> None:
        result = LevelUpResult(new_level=2, physical_points=2, mental_points=1)
        with pytest.raises(AttributeError):
            result.new_level = 5  # type: ignore[misc]

    def test_total_points(self) -> None:
        result = LevelUpResult(new_level=4, physical_points=3, mental_points=2)
        assert result.total_points == 5

    def test_zero_points_level(self) -> None:
        result = LevelUpResult(new_level=3, physical_points=0, mental_points=0)
        assert result.total_points == 0
