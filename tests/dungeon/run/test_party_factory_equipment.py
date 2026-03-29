"""Testes para equipamento inicial via PartyFactory (armor + accessories)."""

from __future__ import annotations

from src.core.classes.class_id import ClassId
from src.core.items.accessory_loader import load_accessories
from src.core.items.armor_loader import load_armors
from src.core.items.weapon_loader import load_weapons
from src.dungeon.run.party_factory import PartyFactory


def _factory() -> PartyFactory:
    return PartyFactory(
        weapon_catalog=load_weapons(),
        armor_catalog=load_armors(),
        accessory_catalog=load_accessories(),
    )


class TestPartyFactoryArmor:

    def test_fighter_starts_with_chain_mail(self) -> None:
        char = _factory().create(ClassId.FIGHTER, "Gareth")
        assert char.armor is not None
        assert char.armor.name == "Chain Mail"

    def test_mage_starts_with_mage_robes(self) -> None:
        char = _factory().create(ClassId.MAGE, "Lyra")
        assert char.armor is not None
        assert char.armor.name == "Mage Robes"


class TestPartyFactoryAccessories:

    def test_mage_starts_with_accessory(self) -> None:
        char = _factory().create(ClassId.MAGE, "Lyra")
        assert len(char.accessories) == 1
        assert char.accessories[0].name == "Amulet of Wisdom"

    def test_barbarian_no_accessories(self) -> None:
        char = _factory().create(ClassId.BARBARIAN, "Krog")
        assert len(char.accessories) == 0


class TestArmorAffectsStats:

    def test_armor_affects_physical_defense(self) -> None:
        """Fighter com chain_mail deve ter physical_defense_bonus incluido."""
        char = _factory().create(ClassId.FIGHTER, "Gareth")
        chain_mail_phys_def = 2
        # Remover armor e comparar
        char.unequip_armor()
        defense_without = char.physical_defense
        # Equipar de volta
        armors = load_armors()
        char.equip_armor(armors["chain_mail"])
        defense_with = char.physical_defense
        assert defense_with == defense_without + chain_mail_phys_def
