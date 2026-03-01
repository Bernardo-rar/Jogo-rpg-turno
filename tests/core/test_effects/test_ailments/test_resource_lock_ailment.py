"""Testes para ResourceLockAilment ABC - base de locks de recurso."""

import pytest

from src.core.effects.ailments.resource_lock_ailment import ResourceLockAilment
from src.core.effects.effect_category import EffectCategory


class TestResourceLockAilmentABC:

    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            ResourceLockAilment(duration=3)  # type: ignore[abstract]

    def test_blocks_mana_skills_is_abstract(self) -> None:

        class _MissingBlocks(ResourceLockAilment):
            @property
            def name(self) -> str:
                return "Test"

            @property
            def ailment_id(self) -> str:
                return "test"

            @property
            def blocks_aura_skills(self) -> bool:
                return False

        with pytest.raises(TypeError):
            _MissingBlocks(duration=3)  # type: ignore[abstract]

    def test_category_is_ailment(self) -> None:

        class _ConcreteLock(ResourceLockAilment):
            @property
            def name(self) -> str:
                return "Test Lock"

            @property
            def ailment_id(self) -> str:
                return "test_lock"

            @property
            def blocks_mana_skills(self) -> bool:
                return True

            @property
            def blocks_aura_skills(self) -> bool:
                return False

        lock = _ConcreteLock(duration=3)
        assert lock.category == EffectCategory.AILMENT

    def test_inherits_effect_lifecycle(self) -> None:

        class _ConcreteLock(ResourceLockAilment):
            @property
            def name(self) -> str:
                return "Test"

            @property
            def ailment_id(self) -> str:
                return "test"

            @property
            def blocks_mana_skills(self) -> bool:
                return False

            @property
            def blocks_aura_skills(self) -> bool:
                return True

        lock = _ConcreteLock(duration=2)
        lock.tick()
        lock.tick()
        assert lock.is_expired
