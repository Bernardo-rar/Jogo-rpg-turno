"""Teste de integração: party real vs monstros Tier 1 no CombatEngine."""

from __future__ import annotations

import json

import pytest

from src.core._paths import resolve_data_path
from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEngine, CombatResult
from src.core.elements.elemental_profile import ElementalProfile, load_profiles
from src.core.items.weapon import Weapon
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_skills
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates


_EMPTY_THRESHOLDS = ThresholdCalculator({})


def _attrs(s: int, d: int, c: int, i: int, w: int, ch: int, m: int) -> Attributes:
    a = Attributes()
    vals = [s, d, c, i, w, ch, m]
    for attr_type, val in zip(AttributeType, vals):
        a.set(attr_type, val)
    return a


def _make_party() -> list[Character]:
    """Cria party simples: Fighter + Mage (2 membros)."""
    fighter_mods = ClassModifiers.from_json("data/classes/fighter.json")
    mage_mods = ClassModifiers.from_json("data/classes/mage.json")
    weapons = load_weapons()
    return [
        Character(
            "Gareth",
            _attrs(10, 8, 7, 3, 4, 3, 3),
            CharacterConfig(
                class_modifiers=fighter_mods,
                threshold_calculator=_EMPTY_THRESHOLDS,
                position=Position.FRONT,
                weapon=weapons["longsword"],
            ),
        ),
        Character(
            "Lyra",
            _attrs(3, 6, 5, 10, 8, 4, 8),
            CharacterConfig(
                class_modifiers=mage_mods,
                threshold_calculator=_EMPTY_THRESHOLDS,
                position=Position.BACK,
                weapon=weapons["arcane_staff"],
            ),
        ),
    ]


def _make_enemy_factory() -> EnemyFactory:
    """Cria EnemyFactory com catalogs reais + enemy-specific."""
    core_weapons = load_weapons()
    dungeon_weapons_path = resolve_data_path("data/dungeon/enemies/weapons.json")
    raw_dw = json.loads(dungeon_weapons_path.read_text(encoding="utf-8"))
    dungeon_weapons = {k: Weapon.from_dict(v) for k, v in raw_dw.items()}
    all_weapons = {**core_weapons, **dungeon_weapons}

    core_profiles = load_profiles()
    dungeon_profiles_path = resolve_data_path(
        "data/dungeon/enemies/elemental_profiles.json",
    )
    raw_dp = json.loads(dungeon_profiles_path.read_text(encoding="utf-8"))
    from src.core.elements.element_type import ElementType
    dungeon_profiles = {
        name: ElementalProfile(
            resistances={ElementType[k]: v for k, v in resists.items()},
        )
        for name, resists in raw_dp.items()
    }
    all_profiles = {**core_profiles, **dungeon_profiles}

    core_skills = load_skills()
    dungeon_skills_path = resolve_data_path(
        "data/dungeon/enemies/skills/tier1_skills.json",
    )
    raw_ds = json.loads(dungeon_skills_path.read_text(encoding="utf-8"))
    dungeon_skills = {
        sid: Skill.from_dict(sid, data) for sid, data in raw_ds.items()
    }
    all_skills = {**core_skills, **dungeon_skills}

    return EnemyFactory(all_weapons, all_profiles, all_skills)


class TestPartyVsTier1:

    def test_combat_runs_to_completion(self) -> None:
        party = _make_party()
        factory = _make_enemy_factory()
        templates = load_tier_templates(tier=1)

        enemies = [
            factory.create(templates["goblin"], suffix="0"),
            factory.create(templates["goblin"], suffix="1"),
            factory.create(templates["skeleton"], suffix="0"),
        ]

        handler = BasicAttackHandler()
        engine = CombatEngine(party, enemies, handler)
        result = engine.run_combat()

        assert result in (CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT)

    def test_all_tier1_monsters_can_be_created(self) -> None:
        factory = _make_enemy_factory()
        templates = load_tier_templates(tier=1)

        for enemy_id, template in templates.items():
            enemy = factory.create(template)
            assert enemy.is_alive
            assert enemy.max_hp > 0
            assert enemy.name == template.name

    def test_five_distinct_monsters(self) -> None:
        factory = _make_enemy_factory()
        templates = load_tier_templates(tier=1)
        assert len(templates) == 5

        names = {t.name for t in templates.values()}
        assert len(names) == 5

    def test_combat_produces_events(self) -> None:
        party = _make_party()
        factory = _make_enemy_factory()
        templates = load_tier_templates(tier=1)

        enemies = [
            factory.create(templates["mushroom"], suffix="0"),
            factory.create(templates["slime"], suffix="0"),
        ]

        handler = BasicAttackHandler()
        engine = CombatEngine(party, enemies, handler)
        engine.run_combat()

        assert len(engine.events) > 0
