"""Testes para accessory_loader."""

from __future__ import annotations

from src.core.items.accessory import Accessory
from src.core.items.accessory_loader import load_accessories
from src.core.items.accessory_type import AccessoryType


class TestAccessoryLoader:
    def test_loads_all_accessories(self) -> None:
        accessories = load_accessories()
        assert len(accessories) >= 4

    def test_returns_dict_of_accessory(self) -> None:
        accessories = load_accessories()
        for acc in accessories.values():
            assert isinstance(acc, Accessory)

    def test_iron_ring_is_ring(self) -> None:
        accessories = load_accessories()
        assert accessories["iron_ring"].accessory_type == AccessoryType.RING

    def test_cloak_of_speed_has_speed_bonus(self) -> None:
        from src.core.effects.modifiable_stat import ModifiableStat
        accessories = load_accessories()
        cloak = accessories["cloak_of_speed"]
        assert cloak.stat_bonuses[0].stat == ModifiableStat.SPEED
