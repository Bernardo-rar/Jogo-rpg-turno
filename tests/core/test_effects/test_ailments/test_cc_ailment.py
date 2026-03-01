"""Testes para CcAilment ABC - base de Crowd Control."""

import pytest

from src.core.effects.ailments.cc_ailment import CcAilment
from src.core.effects.effect_category import EffectCategory
from src.core.effects.tick_result import TickResult


class TestCcAilmentABC:

    def test_can_instantiate_with_defaults(self) -> None:
        cc = CcAilment(duration=3)
        assert cc.is_crowd_control is True
        assert cc.name == "CcAilment"

    def test_is_crowd_control_is_true(self) -> None:

        class _ConcreteCc(CcAilment):
            @property
            def name(self) -> str:
                return "Test CC"

            @property
            def ailment_id(self) -> str:
                return "test_cc"

        cc = _ConcreteCc(duration=3)
        assert cc.is_crowd_control is True

    def test_category_is_ailment(self) -> None:

        class _ConcreteCc(CcAilment):
            @property
            def name(self) -> str:
                return "Test CC"

            @property
            def ailment_id(self) -> str:
                return "test_cc"

        cc = _ConcreteCc(duration=3)
        assert cc.category == EffectCategory.AILMENT

    def test_default_tick_does_not_skip(self) -> None:

        class _ConcreteCc(CcAilment):
            @property
            def name(self) -> str:
                return "Test CC"

            @property
            def ailment_id(self) -> str:
                return "test_cc"

        cc = _ConcreteCc(duration=3)
        result = cc.tick()
        assert result.skip_turn is False
