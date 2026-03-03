"""Testes de integracao: equipar armas no Character."""

from src.core.characters.character import Character
from src.core.classes.cleric.cleric import Cleric
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage
from tests.core.test_items.conftest import (
    ARCANE_STAFF,
    LONGSWORD,
    make_attrs,
    make_item_config,
)


class TestCharacterDefaultWeapon:

    def test_default_weapon_is_none(self) -> None:
        c = Character("Hero", make_attrs(), make_item_config())
        assert c.weapon is None

    def test_config_with_weapon(self) -> None:
        config = make_item_config(weapon=LONGSWORD)
        c = Character("Hero", make_attrs(), config)
        assert c.weapon is LONGSWORD


class TestEquipWeapon:

    def test_equip_sets_weapon(self) -> None:
        c = Character("Hero", make_attrs(), make_item_config())
        c.equip_weapon(LONGSWORD)
        assert c.weapon is LONGSWORD

    def test_equip_replaces_existing(self) -> None:
        config = make_item_config(weapon=LONGSWORD)
        c = Character("Hero", make_attrs(), config)
        c.equip_weapon(ARCANE_STAFF)
        assert c.weapon is ARCANE_STAFF


class TestUnequipWeapon:

    def test_unequip_returns_old_weapon(self) -> None:
        config = make_item_config(weapon=LONGSWORD)
        c = Character("Hero", make_attrs(), config)
        old = c.unequip_weapon()
        assert old is LONGSWORD

    def test_unequip_sets_none(self) -> None:
        config = make_item_config(weapon=LONGSWORD)
        c = Character("Hero", make_attrs(), config)
        c.unequip_weapon()
        assert c.weapon is None

    def test_unequip_when_none_returns_none(self) -> None:
        c = Character("Hero", make_attrs(), make_item_config())
        assert c.unequip_weapon() is None


class TestSubclassWeaponLSP:

    def test_fighter_inherits_weapon(self) -> None:
        f = Fighter("War", make_attrs(), make_item_config())
        f.equip_weapon(LONGSWORD)
        assert f.weapon is LONGSWORD

    def test_mage_inherits_weapon(self) -> None:
        m = Mage("Wiz", make_attrs(), make_item_config())
        m.equip_weapon(ARCANE_STAFF)
        assert m.weapon is ARCANE_STAFF

    def test_cleric_inherits_weapon(self) -> None:
        c = Cleric("Heal", make_attrs(), make_item_config())
        c.equip_weapon(LONGSWORD)
        assert c.weapon is LONGSWORD
