"""Testes para Cold - debuff de speed."""

from src.core.effects.ailments.cold import Cold
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat


class TestColdCreation:

    def test_create_with_duration_and_reduction(self) -> None:
        cold = Cold(duration=3, speed_reduction_percent=20.0)
        assert cold.duration == 3

    def test_name_is_cold(self) -> None:
        cold = Cold(duration=3, speed_reduction_percent=20.0)
        assert cold.name == "Cold"

    def test_ailment_id_is_cold(self) -> None:
        cold = Cold(duration=3, speed_reduction_percent=20.0)
        assert cold.ailment_id == "cold"


class TestColdBehavior:

    def test_modifier_reduces_speed(self) -> None:
        cold = Cold(duration=3, speed_reduction_percent=25.0)
        modifiers = cold.get_modifiers()
        assert len(modifiers) == 1
        assert modifiers[0].stat == ModifiableStat.SPEED
        assert modifiers[0].percent == -25.0

    def test_positive_input_is_negated(self) -> None:
        cold = Cold(duration=3, speed_reduction_percent=25.0)
        assert cold.get_modifiers()[0].percent == -25.0

    def test_category_is_ailment(self) -> None:
        cold = Cold(duration=3, speed_reduction_percent=20.0)
        assert cold.category == EffectCategory.AILMENT


class TestColdWithManager:

    def test_manager_aggregates_speed_modifier(self) -> None:
        manager = EffectManager()
        cold = Cold(duration=3, speed_reduction_percent=20.0)
        manager.add_effect(cold)
        agg = manager.aggregate_modifier(ModifiableStat.SPEED)
        assert agg.percent == -20.0
