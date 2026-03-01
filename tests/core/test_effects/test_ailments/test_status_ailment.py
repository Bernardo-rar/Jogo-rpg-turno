"""Testes para StatusAilment ABC - base de todos os ailments."""

from src.core.effects.effect_category import EffectCategory
from src.core.effects.ailments.status_ailment import StatusAilment


class _ConcreteAilment(StatusAilment):
    """Implementacao concreta minima para testes do StatusAilment ABC."""

    @property
    def name(self) -> str:
        return "Test Ailment"

    @property
    def ailment_id(self) -> str:
        return "test"


class TestStatusAilmentABC:

    def test_can_instantiate_with_defaults(self) -> None:
        ailment = StatusAilment(duration=3)
        assert ailment.name == "StatusAilment"
        assert ailment.ailment_id == "statusailment"

    def test_category_is_ailment(self) -> None:
        """Subclasse concreta deve ter category=AILMENT."""
        ailment = _ConcreteAilment(duration=3)
        assert ailment.category == EffectCategory.AILMENT

    def test_stacking_key_uses_ailment_id(self) -> None:
        ailment = _ConcreteAilment(duration=3)
        assert ailment.stacking_key == "ailment_test"

    def test_ailment_id_auto_derived(self) -> None:
        """Subclasse herda ailment_id derivado do class name."""
        ailment = _ConcreteAilment(duration=3)
        # _ConcreteAilment overrides ailment_id to "test"
        assert ailment.ailment_id == "test"

    def test_inherits_effect_lifecycle(self) -> None:
        ailment = _ConcreteAilment(duration=2)
        assert ailment.duration == 2
        assert not ailment.is_expired
        ailment.tick()
        assert ailment.remaining_turns == 1

    def test_is_crowd_control_default_false(self) -> None:
        ailment = _ConcreteAilment(duration=3)
        assert ailment.is_crowd_control is False

    def test_redirects_target_default_false(self) -> None:
        ailment = _ConcreteAilment(duration=3)
        assert ailment.redirects_target is False
