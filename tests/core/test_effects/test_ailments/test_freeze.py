"""Testes para Freeze - CC que impede acao + reduz cura."""

from src.core.effects.ailments.freeze import Freeze
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat


class TestFreezeCreation:

    def test_create_with_duration(self) -> None:
        freeze = Freeze(duration=2)
        assert freeze.duration == 2

    def test_name_is_freeze(self) -> None:
        freeze = Freeze(duration=2)
        assert freeze.name == "Freeze"

    def test_ailment_id_is_freeze(self) -> None:
        freeze = Freeze(duration=2)
        assert freeze.ailment_id == "freeze"

    def test_is_crowd_control(self) -> None:
        freeze = Freeze(duration=2)
        assert freeze.is_crowd_control is True


class TestFreezeBehavior:

    def test_tick_always_skips_turn(self) -> None:
        freeze = Freeze(duration=3)
        result = freeze.tick()
        assert result.skip_turn is True

    def test_tick_message_mentions_frozen(self) -> None:
        freeze = Freeze(duration=3)
        result = freeze.tick()
        assert "Frozen" in result.message

    def test_get_modifiers_reduces_healing(self) -> None:
        freeze = Freeze(duration=2)
        modifiers = freeze.get_modifiers()
        assert len(modifiers) == 1
        assert modifiers[0].stat == ModifiableStat.HEALING_RECEIVED
        assert modifiers[0].percent < 0

    def test_expires_after_duration(self) -> None:
        freeze = Freeze(duration=2)
        freeze.tick()
        freeze.tick()
        assert freeze.is_expired


class TestFreezeWithManager:

    def test_manager_tick_returns_skip(self) -> None:
        manager = EffectManager()
        freeze = Freeze(duration=2)
        manager.add_effect(freeze)
        results = manager.tick_all()
        assert results[0].skip_turn is True

    def test_manager_aggregates_healing_modifier(self) -> None:
        manager = EffectManager()
        freeze = Freeze(duration=2)
        manager.add_effect(freeze)
        agg = manager.aggregate_modifier(ModifiableStat.HEALING_RECEIVED)
        assert agg.percent < 0
