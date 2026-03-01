"""Testes para Confusion - CC ailment que redireciona ataques."""

from src.core.effects.ailments.confusion import Confusion
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager


class TestConfusionCreation:

    def test_name_is_confusion(self) -> None:
        confusion = Confusion(duration=3)
        assert confusion.name == "Confusion"

    def test_ailment_id(self) -> None:
        confusion = Confusion(duration=3)
        assert confusion.ailment_id == "confusion"

    def test_category_is_ailment(self) -> None:
        confusion = Confusion(duration=3)
        assert confusion.category is EffectCategory.AILMENT

    def test_is_crowd_control(self) -> None:
        confusion = Confusion(duration=3)
        assert confusion.is_crowd_control is True

    def test_stacking_key(self) -> None:
        confusion = Confusion(duration=3)
        assert confusion.stacking_key == "ailment_confusion"


class TestConfusionBehavior:

    def test_redirects_target_is_true(self) -> None:
        confusion = Confusion(duration=3)
        assert confusion.redirects_target is True

    def test_tick_does_not_skip_turn(self) -> None:
        confusion = Confusion(duration=3)
        result = confusion.tick()
        assert result.skip_turn is False

    def test_tick_returns_message(self) -> None:
        confusion = Confusion(duration=3)
        result = confusion.tick()
        assert "Confused" in result.message

    def test_duration_decrements(self) -> None:
        confusion = Confusion(duration=3)
        confusion.tick()
        assert confusion.remaining_turns == 2

    def test_expires_after_duration(self) -> None:
        confusion = Confusion(duration=2)
        confusion.tick()
        confusion.tick()
        assert confusion.is_expired is True


class TestConfusionWithManager:

    def test_manager_tracks_confusion(self) -> None:
        manager = EffectManager()
        confusion = Confusion(duration=3)
        manager.add_effect(confusion)
        assert manager.has_effect("ailment_confusion") is True

    def test_manager_removes_after_expiry(self) -> None:
        manager = EffectManager()
        confusion = Confusion(duration=1)
        manager.add_effect(confusion)
        manager.tick_all()
        assert manager.has_effect("ailment_confusion") is False
