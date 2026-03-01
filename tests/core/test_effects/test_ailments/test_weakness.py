"""Testes para Weakness - reducao de defesa fisica e magica."""

from src.core.effects.ailments.weakness import Weakness
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat


class TestWeaknessCreation:

    def test_create_with_duration_and_reduction(self) -> None:
        weakness = Weakness(duration=3, defense_reduction_percent=20.0)
        assert weakness.duration == 3

    def test_name_is_weakness(self) -> None:
        weakness = Weakness(duration=3, defense_reduction_percent=20.0)
        assert weakness.name == "Weakness"

    def test_ailment_id_is_weakness(self) -> None:
        weakness = Weakness(duration=3, defense_reduction_percent=20.0)
        assert weakness.ailment_id == "weakness"


class TestWeaknessBehavior:

    def test_reduces_physical_defense(self) -> None:
        weakness = Weakness(duration=3, defense_reduction_percent=25.0)
        modifiers = weakness.get_modifiers()
        phys = [m for m in modifiers if m.stat == ModifiableStat.PHYSICAL_DEFENSE]
        assert len(phys) == 1
        assert phys[0].percent == -25.0

    def test_reduces_magical_defense(self) -> None:
        weakness = Weakness(duration=3, defense_reduction_percent=25.0)
        modifiers = weakness.get_modifiers()
        mag = [m for m in modifiers if m.stat == ModifiableStat.MAGICAL_DEFENSE]
        assert len(mag) == 1
        assert mag[0].percent == -25.0

    def test_returns_two_modifiers(self) -> None:
        weakness = Weakness(duration=3, defense_reduction_percent=20.0)
        assert len(weakness.get_modifiers()) == 2

    def test_category_is_ailment(self) -> None:
        weakness = Weakness(duration=3, defense_reduction_percent=20.0)
        assert weakness.category == EffectCategory.AILMENT


class TestWeaknessWithManager:

    def test_manager_aggregates_physical_defense(self) -> None:
        manager = EffectManager()
        weakness = Weakness(duration=3, defense_reduction_percent=20.0)
        manager.add_effect(weakness)
        agg = manager.aggregate_modifier(ModifiableStat.PHYSICAL_DEFENSE)
        assert agg.percent == -20.0

    def test_manager_aggregates_magical_defense(self) -> None:
        manager = EffectManager()
        weakness = Weakness(duration=3, defense_reduction_percent=20.0)
        manager.add_effect(weakness)
        agg = manager.aggregate_modifier(ModifiableStat.MAGICAL_DEFENSE)
        assert agg.percent == -20.0
