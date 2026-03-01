"""Testes para Bleed - DoT de sangramento."""

from src.core.effects.ailments.bleed import Bleed
from src.core.effects.effect_category import EffectCategory


class TestBleedCreation:

    def test_create_with_damage_and_duration(self) -> None:
        bleed = Bleed(damage_per_tick=6, duration=5)
        assert bleed.damage_per_tick == 6
        assert bleed.duration == 5

    def test_name_is_bleed(self) -> None:
        bleed = Bleed(damage_per_tick=6, duration=5)
        assert bleed.name == "Bleed"

    def test_ailment_id_is_bleed(self) -> None:
        bleed = Bleed(damage_per_tick=6, duration=5)
        assert bleed.ailment_id == "bleed"

    def test_stacking_key(self) -> None:
        bleed = Bleed(damage_per_tick=6, duration=5)
        assert bleed.stacking_key == "ailment_bleed"


class TestBleedBehavior:

    def test_tick_deals_damage(self) -> None:
        bleed = Bleed(damage_per_tick=10, duration=3)
        result = bleed.tick()
        assert result.damage == 10

    def test_tick_message_includes_bleed(self) -> None:
        bleed = Bleed(damage_per_tick=10, duration=3)
        result = bleed.tick()
        assert "Bleed" in result.message
