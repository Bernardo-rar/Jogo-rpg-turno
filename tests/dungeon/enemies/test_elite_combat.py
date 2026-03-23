"""Testes de combate: elite vs base — elite deve ser mais forte."""

from __future__ import annotations

import json
from random import Random

from src.core._paths import resolve_data_path
from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile, load_profiles
from src.core.items.weapon import Weapon
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_skills
from src.dungeon.encounters.encounter_factory import EncounterFactory
from src.dungeon.encounters.encounter_template import (
    EncounterSlot,
    EncounterTemplate,
)
from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty
from src.dungeon.enemies.elite_modifier import (
    EliteTierBonuses,
    apply_elite,
    load_elite_bonuses,
)
from src.dungeon.enemies.enemy_archetype import EnemyArchetype
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates

_EMPTY_THRESHOLDS = ThresholdCalculator({})


def _attrs(s: int, d: int, c: int, i: int, w: int, ch: int, m: int) -> Attributes:
    a = Attributes()
    for attr_type, val in zip(AttributeType, [s, d, c, i, w, ch, m]):
        a.set(attr_type, val)
    return a


def _make_catalogs() -> tuple[dict, dict, dict]:
    """Retorna (weapons, profiles, skills) combinados core + dungeon."""
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

    weapons = {**core_weapons, **dungeon_weapons}
    profiles = {**core_profiles, **dungeon_profiles}
    skills = {**core_skills, **dungeon_skills, **elite_skills}
    return weapons, profiles, skills


class TestEliteCombat:

    def test_elite_has_more_hp_than_base(self) -> None:
        weapons, profiles, skills = _make_catalogs()
        factory = EnemyFactory(weapons, profiles, skills)
        templates = load_tier_templates(tier=1)
        goblin = templates["goblin"]
        bonuses = load_elite_bonuses()[1]
        elite_goblin = apply_elite(goblin, bonuses, Random(42))
        base_char = factory.create(goblin)
        elite_char = factory.create(elite_goblin)
        assert elite_char.max_hp > base_char.max_hp

    def test_elite_has_higher_attack(self) -> None:
        weapons, profiles, skills = _make_catalogs()
        factory = EnemyFactory(weapons, profiles, skills)
        templates = load_tier_templates(tier=1)
        goblin = templates["goblin"]
        bonuses = load_elite_bonuses()[1]
        elite_goblin = apply_elite(goblin, bonuses, Random(42))
        base_char = factory.create(goblin)
        elite_char = factory.create(elite_goblin)
        assert elite_char.attack_power > base_char.attack_power

    def test_elite_encounter_slot_produces_elite(self) -> None:
        weapons, profiles, skills = _make_catalogs()
        enemy_factory = EnemyFactory(weapons, profiles, skills)
        elite_bonuses = load_elite_bonuses()
        enc_factory = EncounterFactory(
            enemy_factory,
            load_tier_templates(tier=1),
            elite_bonuses=elite_bonuses,
        )
        template = EncounterTemplate(
            template_id="test_elite",
            difficulty=EncounterDifficulty.ELITE,
            slots=(
                EncounterSlot(archetype=EnemyArchetype.DPS, is_elite=True),
            ),
        )
        result = enc_factory.create(template, rng=Random(42))
        assert len(result.enemies) == 1
        assert result.enemies[0].name.startswith("Elite ")

    def test_elite_encounter_stronger_than_normal(self) -> None:
        weapons, profiles, skills = _make_catalogs()
        enemy_factory = EnemyFactory(weapons, profiles, skills)
        elite_bonuses = load_elite_bonuses()
        pool = load_tier_templates(tier=1)
        normal_factory = EncounterFactory(enemy_factory, pool)
        elite_factory = EncounterFactory(
            enemy_factory, pool, elite_bonuses=elite_bonuses,
        )
        normal_template = EncounterTemplate(
            template_id="normal",
            difficulty=EncounterDifficulty.EASY,
            slots=(EncounterSlot(archetype=EnemyArchetype.DPS),),
        )
        elite_template = EncounterTemplate(
            template_id="elite",
            difficulty=EncounterDifficulty.ELITE,
            slots=(
                EncounterSlot(archetype=EnemyArchetype.DPS, is_elite=True),
            ),
        )
        normal = normal_factory.create(normal_template, rng=Random(42))
        elite = elite_factory.create(elite_template, rng=Random(42))
        assert elite.enemies[0].max_hp > normal.enemies[0].max_hp
