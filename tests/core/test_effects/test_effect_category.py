"""Testes para EffectCategory enum."""

from src.core.effects.effect_category import EffectCategory


class TestEffectCategory:

    def test_buff_value_exists(self) -> None:
        assert isinstance(EffectCategory.BUFF, EffectCategory)

    def test_debuff_value_exists(self) -> None:
        assert isinstance(EffectCategory.DEBUFF, EffectCategory)

    def test_buff_and_debuff_are_different(self) -> None:
        assert EffectCategory.BUFF != EffectCategory.DEBUFF

    def test_ailment_value_exists(self) -> None:
        assert isinstance(EffectCategory.AILMENT, EffectCategory)

    def test_ailment_is_different_from_buff_and_debuff(self) -> None:
        assert EffectCategory.AILMENT != EffectCategory.BUFF
        assert EffectCategory.AILMENT != EffectCategory.DEBUFF
