"""Testes para ArmorWeight enum."""

from __future__ import annotations

from src.core.items.armor_weight import ArmorWeight


class TestArmorWeight:
    def test_has_light(self) -> None:
        assert ArmorWeight.LIGHT is not None

    def test_has_medium(self) -> None:
        assert ArmorWeight.MEDIUM is not None

    def test_has_heavy(self) -> None:
        assert ArmorWeight.HEAVY is not None

    def test_has_three_members(self) -> None:
        assert len(ArmorWeight) == 3
