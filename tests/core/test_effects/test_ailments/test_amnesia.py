"""Testes para Amnesia - bloqueia skills de mana."""

from src.core.effects.ailments.amnesia import Amnesia
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager


class TestAmnesiaCreation:

    def test_create_with_duration(self) -> None:
        amnesia = Amnesia(duration=3)
        assert amnesia.duration == 3

    def test_name_is_amnesia(self) -> None:
        amnesia = Amnesia(duration=3)
        assert amnesia.name == "Amnesia"

    def test_ailment_id_is_amnesia(self) -> None:
        amnesia = Amnesia(duration=3)
        assert amnesia.ailment_id == "amnesia"


class TestAmnesiaBehavior:

    def test_blocks_mana_skills(self) -> None:
        amnesia = Amnesia(duration=3)
        assert amnesia.blocks_mana_skills is True

    def test_does_not_block_aura_skills(self) -> None:
        amnesia = Amnesia(duration=3)
        assert amnesia.blocks_aura_skills is False

    def test_category_is_ailment(self) -> None:
        amnesia = Amnesia(duration=3)
        assert amnesia.category == EffectCategory.AILMENT


class TestAmnesiaWithManager:

    def test_manager_has_effect(self) -> None:
        manager = EffectManager()
        amnesia = Amnesia(duration=3)
        manager.add_effect(amnesia)
        assert manager.has_effect("ailment_amnesia")

    def test_manager_removes_after_expiry(self) -> None:
        manager = EffectManager()
        amnesia = Amnesia(duration=1)
        manager.add_effect(amnesia)
        manager.tick_all()
        assert not manager.has_effect("ailment_amnesia")
