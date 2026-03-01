"""Testes para Poison - DoT de veneno."""

from src.core.effects.ailments.poison import Poison
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager


class TestPoisonCreation:

    def test_create_with_damage_and_duration(self) -> None:
        poison = Poison(damage_per_tick=5, duration=3)
        assert poison.damage_per_tick == 5
        assert poison.duration == 3

    def test_name_is_poison(self) -> None:
        poison = Poison(damage_per_tick=5, duration=3)
        assert poison.name == "Poison"

    def test_ailment_id_is_poison(self) -> None:
        poison = Poison(damage_per_tick=5, duration=3)
        assert poison.ailment_id == "poison"

    def test_stacking_key(self) -> None:
        poison = Poison(damage_per_tick=5, duration=3)
        assert poison.stacking_key == "ailment_poison"


class TestPoisonBehavior:

    def test_tick_deals_damage(self) -> None:
        poison = Poison(damage_per_tick=8, duration=3)
        result = poison.tick()
        assert result.damage == 8

    def test_tick_message_includes_damage(self) -> None:
        poison = Poison(damage_per_tick=8, duration=3)
        result = poison.tick()
        assert "8" in result.message
        assert "Poison" in result.message

    def test_expires_after_duration(self) -> None:
        poison = Poison(damage_per_tick=5, duration=2)
        poison.tick()
        poison.tick()
        assert poison.is_expired

    def test_category_is_ailment(self) -> None:
        poison = Poison(damage_per_tick=5, duration=3)
        assert poison.category == EffectCategory.AILMENT


class TestPoisonWithManager:

    def test_manager_ticks_poison(self) -> None:
        manager = EffectManager()
        poison = Poison(damage_per_tick=5, duration=3)
        manager.add_effect(poison)
        results = manager.tick_all()
        assert len(results) == 1
        assert results[0].damage == 5

    def test_manager_has_effect_by_key(self) -> None:
        manager = EffectManager()
        poison = Poison(damage_per_tick=5, duration=3)
        manager.add_effect(poison)
        assert manager.has_effect("ailment_poison")

    def test_manager_removes_after_expiry(self) -> None:
        manager = EffectManager()
        poison = Poison(damage_per_tick=5, duration=1)
        manager.add_effect(poison)
        manager.tick_all()
        assert not manager.has_effect("ailment_poison")
