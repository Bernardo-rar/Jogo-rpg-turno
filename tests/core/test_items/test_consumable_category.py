"""Testes para ConsumableCategory enum."""

from __future__ import annotations

from src.core.items.consumable_category import ConsumableCategory


class TestConsumableCategory:
    def test_has_healing(self) -> None:
        assert ConsumableCategory.HEALING is not None

    def test_has_defense(self) -> None:
        assert ConsumableCategory.DEFENSE is not None

    def test_has_offensive(self) -> None:
        assert ConsumableCategory.OFFENSIVE is not None

    def test_has_cleanse(self) -> None:
        assert ConsumableCategory.CLEANSE is not None

    def test_has_escape(self) -> None:
        assert ConsumableCategory.ESCAPE is not None

    def test_has_five_members(self) -> None:
        assert len(ConsumableCategory) == 5
