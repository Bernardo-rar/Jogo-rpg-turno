"""Testes para ItemRarity enum."""

from __future__ import annotations

from src.core.items.item_rarity import ItemRarity


class TestItemRarity:
    def test_has_common(self) -> None:
        assert ItemRarity.COMMON is not None

    def test_has_uncommon(self) -> None:
        assert ItemRarity.UNCOMMON is not None

    def test_has_rare(self) -> None:
        assert ItemRarity.RARE is not None

    def test_has_legendary(self) -> None:
        assert ItemRarity.LEGENDARY is not None

    def test_has_four_members(self) -> None:
        assert len(ItemRarity) == 4
