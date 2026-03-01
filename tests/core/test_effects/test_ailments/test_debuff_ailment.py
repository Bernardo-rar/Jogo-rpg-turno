"""Testes para DebuffAilment ABC - base de ailments que reduzem stats."""

import pytest

from src.core.effects.ailments.debuff_ailment import DebuffAilment
from src.core.effects.effect_category import EffectCategory
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier


class TestDebuffAilmentABC:

    def test_can_instantiate_with_defaults(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, percent=-10.0)
        debuff = DebuffAilment(modifiers=[modifier], duration=3)
        assert debuff.name == "DebuffAilment"
        assert debuff.modifier is modifier

    def test_modifier_stored(self) -> None:

        class _ConcreteDebuff(DebuffAilment):
            @property
            def name(self) -> str:
                return "Test Debuff"

            @property
            def ailment_id(self) -> str:
                return "test_debuff"

        modifier = StatModifier(stat=ModifiableStat.SPEED, percent=-15.0)
        debuff = _ConcreteDebuff(modifiers=[modifier], duration=3)
        assert debuff.modifier is modifier

    def test_get_modifiers_returns_modifier(self) -> None:

        class _ConcreteDebuff(DebuffAilment):
            @property
            def name(self) -> str:
                return "Test Debuff"

            @property
            def ailment_id(self) -> str:
                return "test_debuff"

        modifier = StatModifier(stat=ModifiableStat.SPEED, percent=-15.0)
        debuff = _ConcreteDebuff(modifiers=[modifier], duration=3)
        result = debuff.get_modifiers()
        assert len(result) == 1
        assert result[0] is modifier

    def test_positive_flat_raises(self) -> None:

        class _ConcreteDebuff(DebuffAilment):
            @property
            def name(self) -> str:
                return "Test"

            @property
            def ailment_id(self) -> str:
                return "test"

        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        with pytest.raises(ValueError, match="non-positive"):
            _ConcreteDebuff(modifiers=[modifier], duration=3)

    def test_zero_modifier_raises(self) -> None:

        class _ConcreteDebuff(DebuffAilment):
            @property
            def name(self) -> str:
                return "Test"

            @property
            def ailment_id(self) -> str:
                return "test"

        modifier = StatModifier(stat=ModifiableStat.SPEED)
        with pytest.raises(ValueError, match="at least one"):
            _ConcreteDebuff(modifiers=[modifier], duration=3)

    def test_accepts_multiple_modifiers(self) -> None:

        class _ConcreteDebuff(DebuffAilment):
            @property
            def name(self) -> str:
                return "Test"

            @property
            def ailment_id(self) -> str:
                return "test"

        mod1 = StatModifier(stat=ModifiableStat.SPEED, percent=-10.0)
        mod2 = StatModifier(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=-5)
        debuff = _ConcreteDebuff(modifiers=[mod1, mod2], duration=3)
        assert len(debuff.get_modifiers()) == 2

    def test_validates_all_modifiers_in_list(self) -> None:

        class _ConcreteDebuff(DebuffAilment):
            @property
            def name(self) -> str:
                return "Test"

            @property
            def ailment_id(self) -> str:
                return "test"

        good = StatModifier(stat=ModifiableStat.SPEED, percent=-10.0)
        bad = StatModifier(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=5)
        with pytest.raises(ValueError, match="non-positive"):
            _ConcreteDebuff(modifiers=[good, bad], duration=3)

    def test_category_is_ailment(self) -> None:

        class _ConcreteDebuff(DebuffAilment):
            @property
            def name(self) -> str:
                return "Test"

            @property
            def ailment_id(self) -> str:
                return "test"

        modifier = StatModifier(stat=ModifiableStat.SPEED, percent=-10.0)
        debuff = _ConcreteDebuff(modifiers=[modifier], duration=3)
        assert debuff.category == EffectCategory.AILMENT
