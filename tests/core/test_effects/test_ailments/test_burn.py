"""Testes para Burn - DoT de fogo + reducao de cura."""

import pytest

from src.core.effects.ailments.burn import Burn, DEFAULT_HEALING_REDUCTION
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat


class TestBurnCreation:

    def test_create_with_damage_and_duration(self) -> None:
        burn = Burn(damage_per_tick=10, duration=3)
        assert burn.damage_per_tick == 10
        assert burn.duration == 3

    def test_name_is_burn(self) -> None:
        burn = Burn(damage_per_tick=10, duration=3)
        assert burn.name == "Burn"

    def test_ailment_id_is_burn(self) -> None:
        burn = Burn(damage_per_tick=10, duration=3)
        assert burn.ailment_id == "burn"

    def test_default_healing_reduction(self) -> None:
        burn = Burn(damage_per_tick=10, duration=3)
        assert burn.healing_reduction_percent == DEFAULT_HEALING_REDUCTION

    def test_custom_healing_reduction(self) -> None:
        burn = Burn(damage_per_tick=10, duration=3, healing_reduction_percent=50.0)
        assert burn.healing_reduction_percent == 50.0


class TestBurnBehavior:

    def test_tick_deals_damage(self) -> None:
        burn = Burn(damage_per_tick=12, duration=3)
        result = burn.tick()
        assert result.damage == 12

    def test_tick_message_includes_burn(self) -> None:
        burn = Burn(damage_per_tick=12, duration=3)
        result = burn.tick()
        assert "Burn" in result.message

    def test_get_modifiers_returns_healing_received(self) -> None:
        burn = Burn(damage_per_tick=10, duration=3, healing_reduction_percent=30.0)
        modifiers = burn.get_modifiers()
        assert len(modifiers) == 1
        assert modifiers[0].stat == ModifiableStat.HEALING_RECEIVED
        assert modifiers[0].percent == -30.0

    def test_category_is_ailment(self) -> None:
        burn = Burn(damage_per_tick=10, duration=3)
        assert burn.category == EffectCategory.AILMENT


class TestBurnWithManager:

    def test_manager_ticks_burn_damage(self) -> None:
        manager = EffectManager()
        burn = Burn(damage_per_tick=8, duration=3)
        manager.add_effect(burn)
        results = manager.tick_all()
        assert results[0].damage == 8

    def test_manager_aggregates_healing_modifier(self) -> None:
        manager = EffectManager()
        burn = Burn(damage_per_tick=10, duration=3, healing_reduction_percent=25.0)
        manager.add_effect(burn)
        agg = manager.aggregate_modifier(ModifiableStat.HEALING_RECEIVED)
        assert agg.percent == -25.0
