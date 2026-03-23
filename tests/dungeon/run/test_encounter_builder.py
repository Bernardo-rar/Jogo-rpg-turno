"""Testes para EncounterBuilder."""

from __future__ import annotations

import json
from random import Random

from src.core._paths import resolve_data_path
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile, load_profiles
from src.core.items.weapon import Weapon
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_skills
from src.dungeon.encounters.encounter_factory import EncounterFactory
from src.dungeon.enemies.bosses.boss_factory import BossFactory
from src.dungeon.enemies.elite_modifier import load_elite_bonuses
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates
from src.dungeon.map.map_node import MapNode
from src.dungeon.map.room_type import RoomType
from src.dungeon.run.encounter_builder import EncounterBuilder


def _make_builder() -> EncounterBuilder:
    core_weapons = load_weapons()
    raw_dw = json.loads(
        resolve_data_path("data/dungeon/enemies/weapons.json")
        .read_text(encoding="utf-8"),
    )
    dungeon_weapons = {k: Weapon.from_dict(v) for k, v in raw_dw.items()}
    core_profiles = load_profiles()
    raw_dp = json.loads(
        resolve_data_path("data/dungeon/enemies/elemental_profiles.json")
        .read_text(encoding="utf-8"),
    )
    dungeon_profiles = {
        name: ElementalProfile(
            resistances={ElementType[k]: v for k, v in r.items()},
        )
        for name, r in raw_dp.items()
    }
    core_skills = load_skills()
    raw_ds = json.loads(
        resolve_data_path("data/dungeon/enemies/skills/tier1_skills.json")
        .read_text(encoding="utf-8"),
    )
    dungeon_skills = {
        sid: Skill.from_dict(sid, data) for sid, data in raw_ds.items()
    }
    raw_es = json.loads(
        resolve_data_path("data/dungeon/enemies/skills/elite_skills.json")
        .read_text(encoding="utf-8"),
    )
    elite_skills = {
        sid: Skill.from_dict(sid, data) for sid, data in raw_es.items()
    }
    raw_bs = json.loads(
        resolve_data_path("data/dungeon/enemies/skills/boss_skills.json")
        .read_text(encoding="utf-8"),
    )
    boss_skills = {
        sid: Skill.from_dict(sid, data) for sid, data in raw_bs.items()
    }
    weapons = {**core_weapons, **dungeon_weapons}
    profiles = {**core_profiles, **dungeon_profiles}
    skills = {**core_skills, **dungeon_skills, **elite_skills, **boss_skills}
    enemy_factory = EnemyFactory(weapons, profiles, skills)
    elite_bonuses = load_elite_bonuses()
    enc_factory = EncounterFactory(
        enemy_factory, load_tier_templates(tier=1),
        elite_bonuses=elite_bonuses,
    )
    boss_factory = BossFactory(weapons, profiles, skills)
    return EncounterBuilder(enc_factory, boss_factory)


class TestEncounterBuilder:

    def test_build_combat_node(self) -> None:
        builder = _make_builder()
        node = MapNode("L0_N0", 0, RoomType.COMBAT)
        setup = builder.build(node, Random(42))
        assert len(setup.enemies) > 0
        assert setup.is_boss is False

    def test_build_elite_node(self) -> None:
        builder = _make_builder()
        node = MapNode("L1_N0", 1, RoomType.ELITE)
        setup = builder.build(node, Random(42))
        assert len(setup.enemies) > 0

    def test_build_boss_node(self) -> None:
        builder = _make_builder()
        node = MapNode("BOSS", 3, RoomType.BOSS)
        setup = builder.build(node, Random(42))
        assert len(setup.enemies) > 0
        assert setup.is_boss is True
