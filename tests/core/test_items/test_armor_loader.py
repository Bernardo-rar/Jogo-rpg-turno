"""Testes para armor_loader."""

from __future__ import annotations

from src.core.items.armor import Armor
from src.core.items.armor_loader import load_armors
from src.core.items.armor_weight import ArmorWeight


class TestArmorLoader:
    def test_loads_all_armors(self) -> None:
        armors = load_armors()
        assert len(armors) >= 6

    def test_returns_dict_of_armor(self) -> None:
        armors = load_armors()
        for armor in armors.values():
            assert isinstance(armor, Armor)

    def test_leather_armor_is_light(self) -> None:
        armors = load_armors()
        assert armors["leather_armor"].weight == ArmorWeight.LIGHT

    def test_plate_armor_is_heavy(self) -> None:
        armors = load_armors()
        assert armors["plate_armor"].weight == ArmorWeight.HEAVY
