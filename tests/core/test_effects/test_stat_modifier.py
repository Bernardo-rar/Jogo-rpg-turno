"""Testes para StatModifier frozen dataclass."""

import dataclasses

import pytest

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier


class TestStatModifier:
    def test_create_with_flat_only(self):
        mod = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        assert mod.flat == 10
        assert mod.percent == 0.0

    def test_create_with_percent_only(self):
        mod = StatModifier(stat=ModifiableStat.SPEED, percent=20.0)
        assert mod.flat == 0
        assert mod.percent == 20.0

    def test_create_with_both(self):
        mod = StatModifier(
            stat=ModifiableStat.MAGICAL_ATTACK, flat=5, percent=15.0,
        )
        assert mod.flat == 5
        assert mod.percent == 15.0

    def test_default_flat_is_zero(self):
        mod = StatModifier(stat=ModifiableStat.HP_REGEN)
        assert mod.flat == 0

    def test_default_percent_is_zero(self):
        mod = StatModifier(stat=ModifiableStat.HP_REGEN)
        assert mod.percent == 0.0

    def test_is_frozen(self):
        mod = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        assert dataclasses.is_dataclass(mod)
        with pytest.raises(dataclasses.FrozenInstanceError):
            mod.flat = 10  # type: ignore[misc]

    def test_negative_values_for_debuffs(self):
        mod = StatModifier(
            stat=ModifiableStat.PHYSICAL_DEFENSE, flat=-3, percent=-10.0,
        )
        assert mod.flat == -3
        assert mod.percent == -10.0


class TestStatModifierApply:

    def test_apply_flat_only(self):
        mod = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        assert mod.apply(100) == 110

    def test_apply_percent_only(self):
        mod = StatModifier(stat=ModifiableStat.SPEED, percent=20.0)
        assert mod.apply(100) == 120

    def test_apply_flat_and_percent(self):
        mod = StatModifier(
            stat=ModifiableStat.MAGICAL_ATTACK, flat=10, percent=50.0,
        )
        # (100 + 10) * (1.0 + 50.0/100.0) = 110 * 1.5 = 165
        assert mod.apply(100) == 165

    def test_apply_negative_flat_debuff(self):
        mod = StatModifier(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=-20)
        assert mod.apply(100) == 80

    def test_apply_negative_percent_debuff(self):
        mod = StatModifier(stat=ModifiableStat.SPEED, percent=-25.0)
        assert mod.apply(100) == 75

    def test_apply_floors_at_zero(self):
        mod = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=-9999)
        assert mod.apply(50) == 0

    def test_apply_no_modifiers_returns_base(self):
        mod = StatModifier(stat=ModifiableStat.SPEED)
        assert mod.apply(100) == 100

    def test_apply_zero_base_with_flat(self):
        mod = StatModifier(stat=ModifiableStat.SPEED, flat=10)
        assert mod.apply(0) == 10
