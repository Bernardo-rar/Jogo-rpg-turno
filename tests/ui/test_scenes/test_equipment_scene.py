"""Testes para EquipmentScene — logica de equip/unequip e stat preview."""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.damage import DamageType
from src.core.combat.targeting import AttackRange
from src.core.items.armor import Armor
from src.core.items.armor_weight import ArmorWeight
from src.core.items.damage_kind import DamageKind
from src.core.items.weapon import Weapon
from src.core.items.weapon_category import WeaponCategory
from src.core.items.weapon_type import WeaponType
from src.dungeon.loot.drop_table import LootDrop
from src.dungeon.run.equipment_catalog import EquipmentCatalogs
from src.ui.scenes.equipment_scene import (
    EquipmentScene,
    compute_stat_preview,
)

SIMPLE_MODS = ClassModifiers(
    hit_dice=10,
    mod_hp_flat=0,
    mod_hp_mult=1,
    mana_multiplier=1,
    mod_atk_physical=2,
    mod_atk_magical=1,
    mod_def_physical=1,
    mod_def_magical=1,
    regen_hp_mod=0,
    regen_mana_mod=0,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})


def _make_weapon(name: str, weapon_die: int = 8) -> Weapon:
    return Weapon(
        name=name,
        weapon_type=WeaponType.SWORD,
        damage_kind=DamageKind.SLASHING,
        damage_type=DamageType.PHYSICAL,
        weapon_die=weapon_die,
        attack_range=AttackRange.MELEE,
        category=WeaponCategory.MARTIAL,
    )


def _make_armor(name: str, ca_bonus: int = 3) -> Armor:
    return Armor(
        name=name,
        weight=ArmorWeight.LIGHT,
        ca_bonus=ca_bonus,
        hp_bonus=0,
        mana_bonus=0,
        physical_defense_bonus=2,
        magical_defense_bonus=1,
    )


def _build_char(name: str) -> Character:
    attrs = Attributes()
    for at in AttributeType:
        attrs.set(at, 10)
    config = CharacterConfig(
        class_modifiers=SIMPLE_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
    )
    return Character(name, attrs, config)


def _make_catalogs(
    weapons: dict[str, Weapon] | None = None,
    armors: dict[str, Armor] | None = None,
) -> EquipmentCatalogs:
    return EquipmentCatalogs(
        weapons=weapons or {},
        armors=armors or {},
        accessories={},
    )


def _make_scene(
    party: list[Character],
    stash: list[LootDrop],
    catalogs: EquipmentCatalogs,
) -> tuple[EquipmentScene, list[dict]]:
    completed: list[dict] = []
    scene = EquipmentScene(
        fonts=None,
        party=party,
        equipment_stash=stash,
        catalogs=catalogs,
        on_complete=completed.append,
    )
    return scene, completed


class TestEquipWeaponFromStash:

    def test_equip_weapon_from_stash(self) -> None:
        """Weapon moves from stash to character."""
        sword = _make_weapon("Flame Sword")
        catalogs = _make_catalogs(weapons={"flame_sword": sword})
        char = _build_char("Hero")
        stash = [LootDrop(item_type="weapon", item_id="flame_sword")]
        scene, _ = _make_scene([char], stash, catalogs)

        scene.equip_from_stash(char_index=0, slot_index=0, stash_index=0)

        assert char.weapon is not None
        assert char.weapon.name == "Flame Sword"
        assert len(stash) == 0


class TestEquipReplacesOldWeapon:

    def test_equip_replaces_old_weapon(self) -> None:
        """Old weapon returns to stash when new one is equipped."""
        old_sword = _make_weapon("Old Sword", weapon_die=6)
        new_sword = _make_weapon("New Sword", weapon_die=10)
        catalogs = _make_catalogs(
            weapons={"old_sword": old_sword, "new_sword": new_sword},
        )
        char = _build_char("Hero")
        char.equip_weapon(old_sword)
        stash = [LootDrop(item_type="weapon", item_id="new_sword")]
        scene, _ = _make_scene([char], stash, catalogs)

        scene.equip_from_stash(char_index=0, slot_index=0, stash_index=0)

        assert char.weapon is not None
        assert char.weapon.name == "New Sword"
        assert len(stash) == 1
        assert stash[0].item_id == "old_sword"


class TestUnequipReturnsToStash:

    def test_unequip_weapon_returns_to_stash(self) -> None:
        """Unequipping adds item back to stash."""
        sword = _make_weapon("Test Sword")
        catalogs = _make_catalogs(weapons={"test_sword": sword})
        char = _build_char("Hero")
        char.equip_weapon(sword)
        stash: list[LootDrop] = []
        scene, _ = _make_scene([char], stash, catalogs)

        scene.unequip_slot(char_index=0, slot_index=0)

        assert char.weapon is None
        assert len(stash) == 1
        assert stash[0].item_type == "weapon"
        assert stash[0].item_id == "test_sword"

    def test_unequip_armor_returns_to_stash(self) -> None:
        """Unequipping armor adds it back to stash."""
        armor = _make_armor("Leather")
        catalogs = _make_catalogs(armors={"leather": armor})
        char = _build_char("Hero")
        char.equip_armor(armor)
        stash: list[LootDrop] = []
        scene, _ = _make_scene([char], stash, catalogs)

        scene.unequip_slot(char_index=0, slot_index=1)

        assert char.armor is None
        assert len(stash) == 1
        assert stash[0].item_type == "armor"


class TestStatPreviewShowsDifference:

    def test_stat_preview_shows_weapon_difference(self) -> None:
        """Verify stat diff calculation for weapon equip."""
        sword = _make_weapon("Big Sword", weapon_die=12)
        catalogs = _make_catalogs(weapons={"big_sword": sword})
        char = _build_char("Hero")

        preview = compute_stat_preview(
            char, sword, slot_index=0, catalogs=catalogs,
        )
        # Preview should show ATK changing
        atk_entry = next(
            (e for e in preview if e.stat_name == "ATK"), None,
        )
        assert atk_entry is not None
        assert atk_entry.new_value > atk_entry.old_value

    def test_stat_preview_armor_changes_defense(self) -> None:
        """Verify stat diff calculation for armor equip."""
        armor = _make_armor("Plate", ca_bonus=8)
        catalogs = _make_catalogs(armors={"plate": armor})
        char = _build_char("Hero")

        preview = compute_stat_preview(
            char, armor, slot_index=1, catalogs=catalogs,
        )
        # Preview should show DEF changing
        pdef_entry = next(
            (e for e in preview if e.stat_name == "PDEF"), None,
        )
        assert pdef_entry is not None
        assert pdef_entry.new_value > pdef_entry.old_value
