"""Testes para XP table: thresholds de XP por nivel."""

import pytest

from src.core.progression.xp_table import XpTable, level_for_xp, load_xp_table

MAX_LEVEL = 10
MIN_LEVEL = 1


class TestXpTable:
    """Testes do XpTable frozen dataclass."""

    def test_creates_with_thresholds(self) -> None:
        table = XpTable(thresholds=(0, 100, 300))
        assert table.thresholds == (0, 100, 300)

    def test_is_frozen(self) -> None:
        table = XpTable(thresholds=(0, 100))
        with pytest.raises(AttributeError):
            table.thresholds = (0, 200)  # type: ignore[misc]

    def test_max_level(self) -> None:
        table = XpTable(thresholds=(0, 100, 300))
        assert table.max_level == 3

    def test_threshold_for_level(self) -> None:
        table = XpTable(thresholds=(0, 100, 300))
        assert table.threshold_for_level(1) == 0
        assert table.threshold_for_level(2) == 100
        assert table.threshold_for_level(3) == 300

    def test_threshold_for_invalid_level_raises(self) -> None:
        table = XpTable(thresholds=(0, 100))
        with pytest.raises(ValueError):
            table.threshold_for_level(0)
        with pytest.raises(ValueError):
            table.threshold_for_level(3)


class TestLevelForXp:
    """Testes da funcao pura level_for_xp."""

    @pytest.fixture()
    def table(self) -> XpTable:
        return XpTable(thresholds=(0, 100, 300, 600, 1000))

    def test_zero_xp_is_level_1(self, table: XpTable) -> None:
        assert level_for_xp(0, table) == 1

    def test_exact_threshold_levels_up(self, table: XpTable) -> None:
        assert level_for_xp(100, table) == 2
        assert level_for_xp(300, table) == 3
        assert level_for_xp(600, table) == 4
        assert level_for_xp(1000, table) == 5

    def test_between_thresholds_stays_at_lower(self, table: XpTable) -> None:
        assert level_for_xp(50, table) == 1
        assert level_for_xp(99, table) == 1
        assert level_for_xp(150, table) == 2
        assert level_for_xp(999, table) == 4

    def test_above_max_caps_at_max_level(self, table: XpTable) -> None:
        assert level_for_xp(9999, table) == 5

    def test_negative_xp_is_level_1(self, table: XpTable) -> None:
        assert level_for_xp(-10, table) == 1


class TestLoadXpTable:
    """Testes do loader JSON."""

    def test_loads_from_json(self) -> None:
        table = load_xp_table()
        assert isinstance(table, XpTable)
        assert table.max_level == MAX_LEVEL

    def test_first_threshold_is_zero(self) -> None:
        table = load_xp_table()
        assert table.threshold_for_level(MIN_LEVEL) == 0

    def test_thresholds_are_ascending(self) -> None:
        table = load_xp_table()
        for i in range(1, table.max_level):
            lower = table.threshold_for_level(i)
            upper = table.threshold_for_level(i + 1)
            assert upper > lower, f"Level {i+1} threshold must be > level {i}"
