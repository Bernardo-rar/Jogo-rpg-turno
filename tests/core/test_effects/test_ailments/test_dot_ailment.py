"""Testes para DotAilment ABC - base de DoTs."""

import pytest

from src.core.effects.ailments.dot_ailment import DotAilment, MINIMUM_DOT_DAMAGE
from src.core.effects.effect_category import EffectCategory
from src.core.effects.tick_result import TickResult


class _ConcreteDot(DotAilment):
    """Implementacao concreta minima para testes do DotAilment ABC."""

    @property
    def name(self) -> str:
        return "Test DoT"

    @property
    def ailment_id(self) -> str:
        return "test_dot"

    @property
    def tick_message(self) -> str:
        return f"Test deals {self.damage_per_tick} damage"


class _DefaultMessageDot(DotAilment):
    """Subclasse que NAO sobrescreve tick_message (usa default do ABC)."""

    @property
    def name(self) -> str:
        return "TestDot"

    @property
    def ailment_id(self) -> str:
        return "test_dot"


class TestDotAilmentABC:

    def test_can_instantiate_with_defaults(self) -> None:
        dot = DotAilment(damage_per_tick=5, duration=3)
        assert dot.name == "DotAilment"
        assert dot.tick_message == "DotAilment deals 5 damage"

    def test_damage_per_tick_stored(self) -> None:
        dot = _ConcreteDot(damage_per_tick=10, duration=3)
        assert dot.damage_per_tick == 10

    def test_do_tick_returns_damage(self) -> None:
        dot = _ConcreteDot(damage_per_tick=7, duration=3)
        result = dot.tick()
        assert result.damage == 7

    def test_do_tick_returns_message(self) -> None:
        dot = _ConcreteDot(damage_per_tick=5, duration=3)
        result = dot.tick()
        assert result.message == "Test deals 5 damage"

    def test_damage_below_minimum_raises(self) -> None:
        with pytest.raises(ValueError, match="damage_per_tick"):
            _ConcreteDot(damage_per_tick=0, duration=3)

    def test_category_is_ailment(self) -> None:
        dot = _ConcreteDot(damage_per_tick=5, duration=3)
        assert dot.category == EffectCategory.AILMENT

    def test_tick_message_has_default(self) -> None:
        dot = _DefaultMessageDot(damage_per_tick=5, duration=3)
        assert dot.tick_message == "TestDot deals 5 damage"
