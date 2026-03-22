"""Testes para EnemyFactory — cria Character a partir de EnemyTemplate."""

import pytest

from src.core.characters.position import Position
from src.core.combat.damage import DamageType
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile
from src.core.items.weapon import (
    AttackRange,
    DamageKind,
    Weapon,
    WeaponCategory,
    WeaponType,
)
from src.core.skills.skill import Skill
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.combat.action_economy import ActionType
from src.core.skills.target_type import TargetType
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template import EnemyTemplate


_DAGGER = Weapon(
    name="Dagger",
    weapon_type=WeaponType.DAGGER,
    damage_kind=DamageKind.PIERCING,
    damage_type=DamageType.PHYSICAL,
    weapon_die=4,
    attack_range=AttackRange.MELEE,
    category=WeaponCategory.SIMPLE,
)

_GOBLIN_PROFILE = ElementalProfile(
    resistances={ElementType.HOLY: 1.5, ElementType.FIRE: 1.5},
)

_RALLY_SKILL = Skill(
    skill_id="goblin_rally",
    name="Goblin Rally",
    mana_cost=0,
    action_type=ActionType.BONUS_ACTION,
    target_type=TargetType.ALL_ALLIES,
    effects=(
        SkillEffect(
            effect_type=SkillEffectType.BUFF,
            base_power=5,
            duration=2,
        ),
    ),
    slot_cost=1,
)

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
    "skill_ids": ["goblin_rally"],
    "special_traits": ["pack_tactics"],
}


@pytest.fixture()
def factory() -> EnemyFactory:
    return EnemyFactory(
        weapon_catalog={"dagger": _DAGGER},
        profile_catalog={"goblin": _GOBLIN_PROFILE},
        skill_catalog={"goblin_rally": _RALLY_SKILL},
    )


@pytest.fixture()
def template() -> EnemyTemplate:
    return EnemyTemplate.from_dict(_GOBLIN_DICT)


class TestEnemyFactoryCreate:

    def test_creates_character_with_correct_name(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template)
        assert enemy.name == "Goblin"

    def test_creates_with_suffix(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template, suffix="0")
        assert enemy.name == "Goblin_0"

    def test_character_is_alive(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template)
        assert enemy.is_alive

    def test_character_has_correct_position(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template)
        assert enemy.position is Position.FRONT

    def test_character_has_hp(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template)
        assert enemy.max_hp > 0
        assert enemy.current_hp == enemy.max_hp

    def test_character_has_physical_attack(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template)
        assert enemy.physical_attack > 0

    def test_character_has_weapon(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template)
        assert enemy.weapon is not None
        assert enemy.weapon.name == "Dagger"

    def test_character_has_skill_bar(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template)
        assert enemy.skill_bar is not None
        assert len(enemy.skill_bar.all_skills) == 1

    def test_character_preferred_attack_type(
        self, factory: EnemyFactory, template: EnemyTemplate,
    ) -> None:
        enemy = factory.create(template)
        assert enemy.preferred_attack_type is DamageType.PHYSICAL


class TestEnemyFactoryMissingCatalogEntries:

    def test_no_weapon_if_not_in_catalog(self, template: EnemyTemplate) -> None:
        factory = EnemyFactory(
            weapon_catalog={},
            profile_catalog={},
            skill_catalog={},
        )
        enemy = factory.create(template)
        assert enemy.weapon is None

    def test_no_skill_bar_if_skills_not_in_catalog(
        self, template: EnemyTemplate,
    ) -> None:
        factory = EnemyFactory(
            weapon_catalog={},
            profile_catalog={},
            skill_catalog={},
        )
        enemy = factory.create(template)
        assert enemy.skill_bar is None
