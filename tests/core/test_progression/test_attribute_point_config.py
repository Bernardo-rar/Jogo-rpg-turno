"""Testes para configuracao de pontos de atributo por nivel."""

import pytest

from src.core.progression.attribute_point_config import (
    LevelAttributePoints,
    get_points_for_level,
    load_attribute_points,
)


class TestLevelAttributePoints:
    """Testes do LevelAttributePoints frozen dataclass."""

    def test_creates_with_values(self) -> None:
        pts = LevelAttributePoints(physical=2, mental=1)
        assert pts.physical == 2
        assert pts.mental == 1

    def test_is_frozen(self) -> None:
        pts = LevelAttributePoints(physical=2, mental=1)
        with pytest.raises(AttributeError):
            pts.physical = 5  # type: ignore[misc]

    def test_total_points(self) -> None:
        pts = LevelAttributePoints(physical=3, mental=2)
        assert pts.total == 5

    def test_zero_points(self) -> None:
        pts = LevelAttributePoints(physical=0, mental=0)
        assert pts.total == 0


class TestGetPointsForLevel:
    """Testes da funcao get_points_for_level."""

    @pytest.fixture()
    def config(self) -> dict[int, LevelAttributePoints]:
        return {
            2: LevelAttributePoints(physical=2, mental=1),
            4: LevelAttributePoints(physical=3, mental=2),
        }

    def test_returns_points_for_known_level(
        self, config: dict[int, LevelAttributePoints],
    ) -> None:
        result = get_points_for_level(2, config)
        assert result.physical == 2
        assert result.mental == 1

    def test_returns_zero_for_unknown_level(
        self, config: dict[int, LevelAttributePoints],
    ) -> None:
        result = get_points_for_level(3, config)
        assert result.physical == 0
        assert result.mental == 0

    def test_level_1_always_zero(
        self, config: dict[int, LevelAttributePoints],
    ) -> None:
        result = get_points_for_level(1, config)
        assert result.total == 0


class TestLoadAttributePoints:
    """Testes do loader JSON."""

    def test_loads_from_json(self) -> None:
        config = load_attribute_points()
        assert isinstance(config, dict)
        assert len(config) > 0

    def test_all_keys_are_ints(self) -> None:
        config = load_attribute_points()
        for key in config:
            assert isinstance(key, int)

    def test_all_values_are_level_attribute_points(self) -> None:
        config = load_attribute_points()
        for value in config.values():
            assert isinstance(value, LevelAttributePoints)

    def test_level_2_has_points(self) -> None:
        config = load_attribute_points()
        assert config[2].physical > 0

    def test_all_points_non_negative(self) -> None:
        config = load_attribute_points()
        for level, pts in config.items():
            assert pts.physical >= 0, f"Level {level} physical < 0"
            assert pts.mental >= 0, f"Level {level} mental < 0"
