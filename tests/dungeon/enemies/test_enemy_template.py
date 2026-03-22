"""Testes para EnemyTemplate frozen dataclass."""

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.characters.position import Position
from src.core.combat.damage import DamageType
from src.dungeon.enemies.enemy_archetype import EnemyArchetype
from src.dungeon.enemies.enemy_template import EnemyTemplate


_GOBLIN_DICT = {
    "enemy_id": "goblin",
    "name": "Goblin",
    "tier": 1,
    "archetype": "DPS",
    "class_modifiers": {
        "hit_dice": 6,
        "mod_hp_flat": 0,
        "mod_hp_mult": 3,
        "mana_multiplier": 0,
        "mod_atk_physical": 4,
        "mod_atk_magical": 1,
        "mod_def_physical": 2,
        "mod_def_magical": 1,
        "regen_hp_mod": 1,
        "regen_mana_mod": 0,
        "preferred_attack_type": "PHYSICAL",
    },
    "base_attributes": {
        "STRENGTH": 8,
        "DEXTERITY": 14,
        "CONSTITUTION": 6,
        "INTELLIGENCE": 4,
        "WISDOM": 4,
        "CHARISMA": 3,
        "MIND": 2,
    },
    "position": "FRONT",
    "elemental_profile_id": "goblin",
    "weapon_id": "dagger",
    "skill_ids": [],
    "special_traits": ["pack_tactics"],
}


class TestEnemyTemplateFromDict:

    def test_creates_from_valid_dict(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.enemy_id == "goblin"
        assert template.name == "Goblin"

    def test_tier(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.tier == 1

    def test_archetype_is_enum(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.archetype is EnemyArchetype.DPS

    def test_class_modifiers_hit_dice(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.class_modifiers.hit_dice == 6

    def test_class_modifiers_preferred_attack(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.class_modifiers.preferred_attack_type is DamageType.PHYSICAL

    def test_base_attributes(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.base_attributes[AttributeType.DEXTERITY] == 14

    def test_position_is_enum(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.position is Position.FRONT

    def test_elemental_profile_id(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.elemental_profile_id == "goblin"

    def test_weapon_id(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.weapon_id == "dagger"

    def test_special_traits(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.special_traits == ("pack_tactics",)

    def test_skill_ids_empty(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        assert template.skill_ids == ()


class TestEnemyTemplateIsFrozen:

    def test_cannot_mutate(self) -> None:
        template = EnemyTemplate.from_dict(_GOBLIN_DICT)
        with pytest.raises(AttributeError):
            template.name = "Orc"  # type: ignore[misc]


class TestEnemyTemplateDefaults:

    def test_missing_optional_fields_use_defaults(self) -> None:
        minimal = dict(_GOBLIN_DICT)
        del minimal["skill_ids"]
        del minimal["special_traits"]
        del minimal["elemental_profile_id"]
        del minimal["weapon_id"]
        template = EnemyTemplate.from_dict(minimal)
        assert template.skill_ids == ()
        assert template.special_traits == ()
        assert template.elemental_profile_id == "neutral"
        assert template.weapon_id == ""
