"""Testes para stat_effect_helpers - funcoes compartilhadas de validacao."""

import pytest

from src.core.effects.effect import PERMANENT_DURATION
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_effect_helpers import (
    format_stat_name,
    validate_buff_modifier,
    validate_debuff_modifier,
    validate_duration,
)
from src.core.effects.stat_modifier import StatModifier


class TestFormatStatName:

    def test_physical_attack(self) -> None:
        assert format_stat_name(ModifiableStat.PHYSICAL_ATTACK) == "Physical Attack"

    def test_max_hp(self) -> None:
        assert format_stat_name(ModifiableStat.MAX_HP) == "Max HP"

    def test_max_mana(self) -> None:
        assert format_stat_name(ModifiableStat.MAX_MANA) == "Max Mana"

    def test_speed(self) -> None:
        assert format_stat_name(ModifiableStat.SPEED) == "Speed"


class TestValidateDuration:

    def test_valid_duration(self) -> None:
        validate_duration(3)

    def test_permanent_duration(self) -> None:
        validate_duration(PERMANENT_DURATION)

    def test_zero_duration_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid duration"):
            validate_duration(0)


class TestValidateBuffModifier:

    def test_valid_flat_buff(self) -> None:
        mod = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        validate_buff_modifier(mod)

    def test_negative_flat_raises(self) -> None:
        mod = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        with pytest.raises(ValueError, match="non-negative"):
            validate_buff_modifier(mod)

    def test_zero_modifier_raises(self) -> None:
        mod = StatModifier(stat=ModifiableStat.SPEED)
        with pytest.raises(ValueError, match="at least one"):
            validate_buff_modifier(mod)


class TestValidateDebuffModifier:

    def test_valid_negative_percent(self) -> None:
        mod = StatModifier(stat=ModifiableStat.SPEED, percent=-10.0)
        validate_debuff_modifier(mod)

    def test_positive_flat_raises(self) -> None:
        mod = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        with pytest.raises(ValueError, match="non-positive"):
            validate_debuff_modifier(mod)

    def test_zero_modifier_raises(self) -> None:
        mod = StatModifier(stat=ModifiableStat.SPEED)
        with pytest.raises(ValueError, match="at least one"):
            validate_debuff_modifier(mod)
