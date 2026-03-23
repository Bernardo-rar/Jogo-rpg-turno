"""Testes para PartyFactory."""

from __future__ import annotations

from src.core.characters.character import Character
from src.core.characters.position import Position
from src.core.classes.class_id import ClassId
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage
from src.core.items.weapon_loader import load_weapons
from src.dungeon.run.party_factory import PartyFactory, is_frontliner


def _factory() -> PartyFactory:
    return PartyFactory(weapon_catalog=load_weapons())


class TestPartyFactory:

    def test_create_fighter(self) -> None:
        f = _factory()
        char = f.create(ClassId.FIGHTER, "Gareth")
        assert isinstance(char, Fighter)
        assert char.name == "Gareth"

    def test_create_mage(self) -> None:
        f = _factory()
        char = f.create(ClassId.MAGE, "Lyra")
        assert isinstance(char, Mage)

    def test_all_13_classes(self) -> None:
        f = _factory()
        for cid in ClassId:
            char = f.create(cid, f"Test_{cid.value}")
            assert isinstance(char, Character)
            assert char.is_alive

    def test_has_weapon(self) -> None:
        f = _factory()
        char = f.create(ClassId.FIGHTER, "F")
        assert char.weapon is not None

    def test_fighter_position_front(self) -> None:
        f = _factory()
        char = f.create(ClassId.FIGHTER, "F")
        assert char.position == Position.FRONT

    def test_mage_position_back(self) -> None:
        f = _factory()
        char = f.create(ClassId.MAGE, "M")
        assert char.position == Position.BACK

    def test_has_hp(self) -> None:
        f = _factory()
        char = f.create(ClassId.CLERIC, "C")
        assert char.max_hp > 0
        assert char.current_hp == char.max_hp


class TestIsFrontliner:

    def test_fighter_is_front(self) -> None:
        assert is_frontliner(ClassId.FIGHTER) is True

    def test_mage_is_not_front(self) -> None:
        assert is_frontliner(ClassId.MAGE) is False

    def test_paladin_is_front(self) -> None:
        assert is_frontliner(ClassId.PALADIN) is True
