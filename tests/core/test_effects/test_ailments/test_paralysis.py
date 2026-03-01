"""Testes para Paralysis - CC com chance de perder acao."""

from src.core.effects.ailments.paralysis import Paralysis, DEFAULT_SKIP_CHANCE
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager


class TestParalysisCreation:

    def test_create_with_duration(self) -> None:
        para = Paralysis(duration=3)
        assert para.duration == 3

    def test_name_is_paralysis(self) -> None:
        para = Paralysis(duration=3)
        assert para.name == "Paralysis"

    def test_ailment_id_is_paralysis(self) -> None:
        para = Paralysis(duration=3)
        assert para.ailment_id == "paralysis"

    def test_default_skip_chance(self) -> None:
        para = Paralysis(duration=3)
        assert para.skip_chance == DEFAULT_SKIP_CHANCE

    def test_custom_skip_chance(self) -> None:
        para = Paralysis(duration=3, skip_chance=0.75)
        assert para.skip_chance == 0.75

    def test_is_crowd_control(self) -> None:
        para = Paralysis(duration=3)
        assert para.is_crowd_control is True


class TestParalysisBehavior:

    def test_always_skips_when_random_below_chance(self) -> None:
        para = Paralysis(duration=3, skip_chance=0.5, random_fn=lambda: 0.1)
        result = para.tick()
        assert result.skip_turn is True

    def test_never_skips_when_random_above_chance(self) -> None:
        para = Paralysis(duration=3, skip_chance=0.5, random_fn=lambda: 0.9)
        result = para.tick()
        assert result.skip_turn is False

    def test_skip_message_when_paralyzed(self) -> None:
        para = Paralysis(duration=3, random_fn=lambda: 0.0)
        result = para.tick()
        assert "Paralyzed" in result.message

    def test_resist_message_when_not_paralyzed(self) -> None:
        para = Paralysis(duration=3, random_fn=lambda: 1.0)
        result = para.tick()
        assert "Resisted" in result.message


class TestParalysisWithManager:

    def test_manager_tick_can_skip(self) -> None:
        manager = EffectManager()
        para = Paralysis(duration=3, random_fn=lambda: 0.0)
        manager.add_effect(para)
        results = manager.tick_all()
        assert results[0].skip_turn is True

    def test_manager_has_effect(self) -> None:
        manager = EffectManager()
        para = Paralysis(duration=3)
        manager.add_effect(para)
        assert manager.has_effect("ailment_paralysis")
