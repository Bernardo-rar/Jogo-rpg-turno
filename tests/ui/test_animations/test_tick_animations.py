"""Testes para tick_animation_factory."""

from src.core.combat.effect_phase import EffectLogEntry
from src.ui.animations.floating_text import FloatingText
from src.ui.animations.heal_particles import HealParticles
from src.ui.animations.poison_bubbles import PoisonBubbles
from src.ui.animations.tick_animation_factory import create_tick_animations

_RECT = (100, 50, 160, 110)


class TestTickAnimations:
    def test_tick_damage_creates_poison_and_text(self) -> None:
        entry = EffectLogEntry(
            round_number=1, character_name="Hero", value=5,
            message="poison damage (5)",
        )
        anims = create_tick_animations(entry, _RECT)
        types = [type(a) for a in anims]
        assert PoisonBubbles in types
        assert FloatingText in types

    def test_tick_heal_creates_particles_and_text(self) -> None:
        entry = EffectLogEntry(
            round_number=1, character_name="Hero", value=8,
            message="regen heal (8)",
        )
        anims = create_tick_animations(entry, _RECT)
        types = [type(a) for a in anims]
        assert HealParticles in types
        assert FloatingText in types

    def test_tick_skip_creates_nothing(self) -> None:
        entry = EffectLogEntry(
            round_number=1, character_name="Hero", value=0,
            message="frozen", is_skip=True,
        )
        anims = create_tick_animations(entry, _RECT)
        assert anims == []

    def test_tick_zero_value_creates_nothing(self) -> None:
        entry = EffectLogEntry(
            round_number=1, character_name="Hero", value=0,
            message="poison damage (0)",
        )
        anims = create_tick_animations(entry, _RECT)
        assert anims == []

    def test_tick_damage_text_shows_value(self) -> None:
        entry = EffectLogEntry(
            round_number=1, character_name="Hero", value=12,
            message="burn damage (12)",
        )
        anims = create_tick_animations(entry, _RECT)
        texts = [a for a in anims if isinstance(a, FloatingText)]
        assert len(texts) == 1
        assert "12" in texts[0].text
