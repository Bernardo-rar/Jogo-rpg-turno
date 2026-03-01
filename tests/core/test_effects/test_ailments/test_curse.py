"""Testes para Curse - bloqueia skills de aura."""

from src.core.effects.ailments.curse import Curse
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager


class TestCurseCreation:

    def test_create_with_duration(self) -> None:
        curse = Curse(duration=4)
        assert curse.duration == 4

    def test_name_is_curse(self) -> None:
        curse = Curse(duration=4)
        assert curse.name == "Curse"

    def test_ailment_id_is_curse(self) -> None:
        curse = Curse(duration=4)
        assert curse.ailment_id == "curse"


class TestCurseBehavior:

    def test_blocks_aura_skills(self) -> None:
        curse = Curse(duration=3)
        assert curse.blocks_aura_skills is True

    def test_does_not_block_mana_skills(self) -> None:
        curse = Curse(duration=3)
        assert curse.blocks_mana_skills is False

    def test_category_is_ailment(self) -> None:
        curse = Curse(duration=3)
        assert curse.category == EffectCategory.AILMENT


class TestCurseWithManager:

    def test_manager_has_effect(self) -> None:
        manager = EffectManager()
        curse = Curse(duration=3)
        manager.add_effect(curse)
        assert manager.has_effect("ailment_curse")

    def test_manager_removes_after_expiry(self) -> None:
        manager = EffectManager()
        curse = Curse(duration=1)
        manager.add_effect(curse)
        manager.tick_all()
        assert not manager.has_effect("ailment_curse")
