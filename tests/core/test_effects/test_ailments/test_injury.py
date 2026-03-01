"""Testes para Injury - reducao de ataque fisico e magico."""

from src.core.effects.ailments.injury import Injury
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat


class TestInjuryCreation:

    def test_create_with_duration_and_reduction(self) -> None:
        injury = Injury(duration=3, attack_reduction_percent=15.0)
        assert injury.duration == 3

    def test_name_is_injury(self) -> None:
        injury = Injury(duration=3, attack_reduction_percent=15.0)
        assert injury.name == "Injury"

    def test_ailment_id_is_injury(self) -> None:
        injury = Injury(duration=3, attack_reduction_percent=15.0)
        assert injury.ailment_id == "injury"


class TestInjuryBehavior:

    def test_reduces_physical_attack(self) -> None:
        injury = Injury(duration=3, attack_reduction_percent=20.0)
        modifiers = injury.get_modifiers()
        phys = [m for m in modifiers if m.stat == ModifiableStat.PHYSICAL_ATTACK]
        assert len(phys) == 1
        assert phys[0].percent == -20.0

    def test_reduces_magical_attack(self) -> None:
        injury = Injury(duration=3, attack_reduction_percent=20.0)
        modifiers = injury.get_modifiers()
        mag = [m for m in modifiers if m.stat == ModifiableStat.MAGICAL_ATTACK]
        assert len(mag) == 1
        assert mag[0].percent == -20.0

    def test_returns_two_modifiers(self) -> None:
        injury = Injury(duration=3, attack_reduction_percent=15.0)
        assert len(injury.get_modifiers()) == 2

    def test_category_is_ailment(self) -> None:
        injury = Injury(duration=3, attack_reduction_percent=15.0)
        assert injury.category == EffectCategory.AILMENT


class TestInjuryWithManager:

    def test_manager_aggregates_physical_attack(self) -> None:
        manager = EffectManager()
        injury = Injury(duration=3, attack_reduction_percent=20.0)
        manager.add_effect(injury)
        agg = manager.aggregate_modifier(ModifiableStat.PHYSICAL_ATTACK)
        assert agg.percent == -20.0

    def test_manager_aggregates_magical_attack(self) -> None:
        manager = EffectManager()
        injury = Injury(duration=3, attack_reduction_percent=20.0)
        manager.add_effect(injury)
        agg = manager.aggregate_modifier(ModifiableStat.MAGICAL_ATTACK)
        assert agg.percent == -20.0
