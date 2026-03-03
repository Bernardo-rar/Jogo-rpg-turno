"""Testes de integracao: armas + combate end-to-end."""

from src.core.characters.character import Character
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEngine, CombatResult
from src.core.combat.damage import DamageType, resolve_damage
from src.core.combat.targeting import AttackRange
from src.core.elements.element_type import ElementType
from src.core.items.damage_kind import DamageKind
from src.core.items.weapon import Weapon
from src.core.items.weapon_category import WeaponCategory
from src.core.items.weapon_loader import load_weapons
from src.core.items.weapon_proficiency import (
    FIGHTER_PROFICIENCIES,
    MAGE_PROFICIENCIES,
    can_equip,
)
from src.core.items.weapon_type import WeaponType
from tests.core.test_items.conftest import LONGSWORD, make_attrs, make_item_config


class TestArmedVsUnarmedDamage:

    def test_armed_deals_more_damage(self) -> None:
        unarmed = Character("A", make_attrs(), make_item_config())
        armed = Character("B", make_attrs(), make_item_config(weapon=LONGSWORD))
        target = Character("T", make_attrs(), make_item_config())
        result_u = resolve_damage(unarmed.physical_attack, target.physical_defense)
        result_a = resolve_damage(armed.physical_attack, target.physical_defense)
        assert result_a.final_damage > result_u.final_damage


class TestElementalWeaponRetainsElement:

    def test_weapon_element_accessible(self) -> None:
        flame = Weapon(
            name="Flame Sword",
            weapon_type=WeaponType.SWORD,
            damage_kind=DamageKind.SLASHING,
            damage_type=DamageType.PHYSICAL,
            weapon_die=10,
            attack_range=AttackRange.MELEE,
            category=WeaponCategory.MARTIAL,
            element=ElementType.FIRE,
        )
        c = Character("A", make_attrs(), make_item_config(weapon=flame))
        assert c.weapon is not None
        assert c.weapon.element == ElementType.FIRE


class TestWeaponSwapChangesStats:

    def test_swap_updates_attack(self) -> None:
        staff = Weapon(
            name="Staff",
            weapon_type=WeaponType.STAFF,
            damage_kind=DamageKind.BLUDGEONING,
            damage_type=DamageType.MAGICAL,
            weapon_die=8,
            attack_range=AttackRange.RANGED,
            category=WeaponCategory.MAGICAL,
        )
        c = Character("A", make_attrs(), make_item_config(weapon=LONGSWORD))
        phys_armed = c.physical_attack
        c.equip_weapon(staff)
        assert c.physical_attack < phys_armed
        assert c.magical_attack > 100


class TestProficiencyCheckBeforeEquip:

    def test_fighter_can_equip_martial(self) -> None:
        weapons = load_weapons()
        assert can_equip(weapons["longsword"], FIGHTER_PROFICIENCIES)

    def test_mage_cannot_equip_martial(self) -> None:
        weapons = load_weapons()
        assert not can_equip(weapons["longsword"], MAGE_PROFICIENCIES)

    def test_mage_can_equip_magical(self) -> None:
        weapons = load_weapons()
        assert can_equip(weapons["arcane_staff"], MAGE_PROFICIENCIES)


class TestMockBattleWithWeapons:

    def test_armed_battle_runs_to_completion(self) -> None:
        party_a = [
            Character(
                f"Hero_{i}", make_attrs(12),
                make_item_config(weapon=LONGSWORD),
            )
            for i in range(2)
        ]
        party_b = [
            Character(
                f"Goblin_{i}", make_attrs(8),
                make_item_config(),
            )
            for i in range(2)
        ]
        engine = CombatEngine(party_a, party_b, BasicAttackHandler())
        result = engine.run_combat()
        assert result in (CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT)
