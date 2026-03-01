"""Testes para Sickness - reducao de cura recebida."""

from src.core.effects.ailments.sickness import Sickness
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat


class TestSicknessCreation:

    def test_create_with_duration_and_reduction(self) -> None:
        sickness = Sickness(duration=4, recovery_reduction_percent=30.0)
        assert sickness.duration == 4

    def test_name_is_sickness(self) -> None:
        sickness = Sickness(duration=4, recovery_reduction_percent=30.0)
        assert sickness.name == "Sickness"

    def test_ailment_id_is_sickness(self) -> None:
        sickness = Sickness(duration=4, recovery_reduction_percent=30.0)
        assert sickness.ailment_id == "sickness"


class TestSicknessBehavior:

    def test_modifier_reduces_healing_received(self) -> None:
        sickness = Sickness(duration=3, recovery_reduction_percent=40.0)
        modifiers = sickness.get_modifiers()
        assert len(modifiers) == 1
        assert modifiers[0].stat == ModifiableStat.HEALING_RECEIVED
        assert modifiers[0].percent == -40.0

    def test_category_is_ailment(self) -> None:
        sickness = Sickness(duration=3, recovery_reduction_percent=30.0)
        assert sickness.category == EffectCategory.AILMENT


class TestSicknessWithManager:

    def test_manager_aggregates_healing_modifier(self) -> None:
        manager = EffectManager()
        sickness = Sickness(duration=3, recovery_reduction_percent=35.0)
        manager.add_effect(sickness)
        agg = manager.aggregate_modifier(ModifiableStat.HEALING_RECEIVED)
        assert agg.percent == -35.0
