"""Testes para AccessoryType enum."""

from __future__ import annotations

from src.core.items.accessory_type import AccessoryType


class TestAccessoryType:
    def test_has_amulet(self) -> None:
        assert AccessoryType.AMULET is not None

    def test_has_ring(self) -> None:
        assert AccessoryType.RING is not None

    def test_has_cloak(self) -> None:
        assert AccessoryType.CLOAK is not None

    def test_has_bracelet(self) -> None:
        assert AccessoryType.BRACELET is not None

    def test_has_four_members(self) -> None:
        assert len(AccessoryType) == 4
