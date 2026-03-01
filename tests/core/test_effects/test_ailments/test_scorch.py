"""Testes para Scorch - DoT massivo + reducao cumulativa de MAX_HP."""

import pytest

from src.core.effects.ailments.scorch import Scorch, DEFAULT_MAX_HP_REDUCTION
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stacking import StackingPolicy


class TestScorchCreation:

    def test_create_with_damage_and_duration(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3)
        assert scorch.damage_per_tick == 20
        assert scorch.duration == 3

    def test_name_is_scorch(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3)
        assert scorch.name == "Scorch"

    def test_ailment_id_is_scorch(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3)
        assert scorch.ailment_id == "scorch"

    def test_default_max_hp_reduction(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3)
        assert scorch.max_hp_reduction == DEFAULT_MAX_HP_REDUCTION

    def test_custom_max_hp_reduction(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3, max_hp_reduction=25)
        assert scorch.max_hp_reduction == 25


class TestScorchBehavior:

    def test_tick_deals_damage(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3)
        result = scorch.tick()
        assert result.damage == 20

    def test_tick_message_includes_scorch(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3)
        result = scorch.tick()
        assert "Scorch" in result.message

    def test_get_modifiers_returns_max_hp_reduction(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3, max_hp_reduction=15)
        modifiers = scorch.get_modifiers()
        assert len(modifiers) == 1
        assert modifiers[0].stat == ModifiableStat.MAX_HP
        assert modifiers[0].flat == -15

    def test_category_is_ailment(self) -> None:
        scorch = Scorch(damage_per_tick=20, duration=3)
        assert scorch.category == EffectCategory.AILMENT


class TestScorchWithManager:

    def test_manager_ticks_scorch_damage(self) -> None:
        manager = EffectManager()
        scorch = Scorch(damage_per_tick=20, duration=3)
        manager.add_effect(scorch)
        results = manager.tick_all()
        assert results[0].damage == 20

    def test_manager_aggregates_max_hp_modifier(self) -> None:
        manager = EffectManager()
        scorch = Scorch(damage_per_tick=20, duration=3, max_hp_reduction=10)
        manager.add_effect(scorch)
        agg = manager.aggregate_modifier(ModifiableStat.MAX_HP)
        assert agg.flat == -10

    def test_stacking_accumulates_max_hp_reduction(self) -> None:
        manager = EffectManager()
        manager.set_stacking_policy("ailment_scorch", StackingPolicy.STACK)
        scorch1 = Scorch(damage_per_tick=20, duration=3, max_hp_reduction=10)
        scorch2 = Scorch(damage_per_tick=20, duration=3, max_hp_reduction=10)
        manager.add_effect(scorch1)
        manager.add_effect(scorch2)
        assert manager.count == 2
        agg = manager.aggregate_modifier(ModifiableStat.MAX_HP)
        assert agg.flat == -20
