"""Testes para StatBonus frozen dataclass."""

from __future__ import annotations

import pytest

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.items.stat_bonus import StatBonus


class TestStatBonusCreation:
    def test_create_with_flat(self) -> None:
        sb = StatBonus(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=5)
        assert sb.stat == ModifiableStat.PHYSICAL_DEFENSE
        assert sb.flat == 5
        assert sb.percent == 0.0

    def test_create_with_percent(self) -> None:
        sb = StatBonus(stat=ModifiableStat.SPEED, percent=10.0)
        assert sb.percent == pytest.approx(10.0)
        assert sb.flat == 0

    def test_create_with_both(self) -> None:
        sb = StatBonus(
            stat=ModifiableStat.MAX_HP, flat=10, percent=5.0,
        )
        assert sb.flat == 10
        assert sb.percent == pytest.approx(5.0)

    def test_is_frozen(self) -> None:
        sb = StatBonus(stat=ModifiableStat.SPEED, flat=2)
        with pytest.raises(AttributeError):
            sb.flat = 10  # type: ignore[misc]


class TestStatBonusFromDict:
    def test_from_dict_flat_only(self) -> None:
        data: dict[str, object] = {"stat": "PHYSICAL_DEFENSE", "flat": 5}
        sb = StatBonus.from_dict(data)
        assert sb.stat == ModifiableStat.PHYSICAL_DEFENSE
        assert sb.flat == 5
        assert sb.percent == 0.0

    def test_from_dict_with_percent(self) -> None:
        data: dict[str, object] = {
            "stat": "MAGICAL_DEFENSE", "flat": 3, "percent": 10.0,
        }
        sb = StatBonus.from_dict(data)
        assert sb.stat == ModifiableStat.MAGICAL_DEFENSE
        assert sb.flat == 3
        assert sb.percent == pytest.approx(10.0)
