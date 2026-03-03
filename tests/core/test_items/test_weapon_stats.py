"""Testes para weapon_die routing no CombatStatsMixin."""

from src.core.characters.character import Character
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage
from tests.core.test_items.conftest import (
    ARCANE_STAFF,
    LONGSWORD,
    make_attrs,
    make_item_config,
)


class TestPhysicalWeaponDie:

    def test_without_weapon_uses_zero(self) -> None:
        c = Character("A", make_attrs(), make_item_config())
        unarmed_atk = c.physical_attack
        # (0 + STR + DEX) * mod = (0 + 10 + 10) * 5 = 100
        assert unarmed_atk == 100

    def test_physical_weapon_adds_die(self) -> None:
        config = make_item_config(weapon=LONGSWORD)
        c = Character("A", make_attrs(), config)
        # (8 + 10 + 10) * 5 = 140
        assert c.physical_attack == 140

    def test_magical_weapon_does_not_add_to_physical(self) -> None:
        config = make_item_config(weapon=ARCANE_STAFF)
        c = Character("A", make_attrs(), config)
        # Staff is MAGICAL, so physical_attack stays (0 + 10 + 10) * 5
        assert c.physical_attack == 100


class TestMagicalWeaponDie:

    def test_without_weapon_uses_zero(self) -> None:
        c = Character("A", make_attrs(), make_item_config())
        # (0 + WIS + INT) * mod = (0 + 10 + 10) * 5 = 100
        assert c.magical_attack == 100

    def test_magical_weapon_adds_die(self) -> None:
        config = make_item_config(weapon=ARCANE_STAFF)
        c = Character("A", make_attrs(), config)
        # (8 + 10 + 10) * 5 = 140
        assert c.magical_attack == 140

    def test_physical_weapon_does_not_add_to_magical(self) -> None:
        config = make_item_config(weapon=LONGSWORD)
        c = Character("A", make_attrs(), config)
        # Sword is PHYSICAL, so magical_attack stays (0 + 10 + 10) * 5
        assert c.magical_attack == 100


class TestEquipChangesStats:

    def test_equip_increases_attack(self) -> None:
        c = Character("A", make_attrs(), make_item_config())
        before = c.physical_attack
        c.equip_weapon(LONGSWORD)
        assert c.physical_attack > before

    def test_unequip_resets_attack(self) -> None:
        config = make_item_config(weapon=LONGSWORD)
        c = Character("A", make_attrs(), config)
        armed = c.physical_attack
        c.unequip_weapon()
        assert c.physical_attack < armed


class TestSubclassOverrideWithWeapon:

    def test_fighter_physical_includes_weapon(self) -> None:
        config = make_item_config(weapon=LONGSWORD)
        f = Fighter("War", make_attrs(), config)
        # Fighter applies stance multiplier on top of base
        assert f.physical_attack > 0

    def test_mage_magical_includes_weapon(self) -> None:
        config = make_item_config(weapon=ARCANE_STAFF)
        m = Mage("Wiz", make_attrs(), config)
        assert m.magical_attack > 0
