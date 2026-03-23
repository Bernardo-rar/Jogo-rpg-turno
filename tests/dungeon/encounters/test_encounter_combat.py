"""Teste de integracao: encounter gerado roda combate ate o fim."""

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
from src.core.combat.combat_engine import CombatEngine, CombatResult
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile, load_profiles
from src.core.items.weapon import Weapon
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_skills
from src.dungeon.encounters.encounter_factory import EncounterFactory
from src.dungeon.encounters.encounter_template_loader import (
    load_encounter_templates,
    load_templates_by_difficulty,
)
from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates

_EMPTY_THRESHOLDS = ThresholdCalculator({})


def _attrs(s: int, d: int, c: int, i: int, w: int, ch: int, m: int) -> Attributes:
    a = Attributes()
    for attr_type, val in zip(AttributeType, vals := [s, d, c, i, w, ch, m]):
        a.set(attr_type, val)
    return a


def _make_party() -> list[Character]:
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


def _make_encounter_factory() -> EncounterFactory:
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

    enemy_factory = EnemyFactory(
        {**core_weapons, **dungeon_weapons},
        {**core_profiles, **dungeon_profiles},
        {**core_skills, **dungeon_skills},
    )
    return EncounterFactory(enemy_factory, load_tier_templates(tier=1))


class TestEncounterCombat:

    def test_easy_encounter_runs_to_completion(self) -> None:
        party = _make_party()
        enc_factory = _make_encounter_factory()
        templates = load_encounter_templates()
        encounter = enc_factory.create(templates["easy_3dps"], rng=Random(42))
        engine = CombatEngine(
            party, list(encounter.enemies), encounter.handler,
        )
        result = engine.run_combat()
        assert result in (CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT)

    def test_medium_encounter_runs(self) -> None:
        party = _make_party()
        enc_factory = _make_encounter_factory()
        templates = load_encounter_templates()
        encounter = enc_factory.create(
            templates["medium_tank_2dps"], rng=Random(42),
        )
        engine = CombatEngine(
            party, list(encounter.enemies), encounter.handler,
        )
        result = engine.run_combat()
        assert result in (CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT)

    def test_hard_encounter_runs(self) -> None:
        party = _make_party()
        enc_factory = _make_encounter_factory()
        templates = load_encounter_templates()
        encounter = enc_factory.create(
            templates["hard_full"], rng=Random(42),
        )
        engine = CombatEngine(
            party, list(encounter.enemies), encounter.handler,
        )
        result = engine.run_combat()
        assert result in (CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT)

    def test_encounter_produces_events(self) -> None:
        party = _make_party()
        enc_factory = _make_encounter_factory()
        templates = load_encounter_templates()
        encounter = enc_factory.create(templates["easy_3dps"], rng=Random(42))
        engine = CombatEngine(
            party, list(encounter.enemies), encounter.handler,
        )
        engine.run_combat()
        assert len(engine.events) > 0

    def test_no_draw_result(self) -> None:
        """Encounters com AI nao devem terminar em DRAW."""
        party = _make_party()
        enc_factory = _make_encounter_factory()
        templates = load_encounter_templates()
        encounter = enc_factory.create(
            templates["easy_2dps_tank"], rng=Random(42),
        )
        engine = CombatEngine(
            party, list(encounter.enemies), encounter.handler,
        )
        result = engine.run_combat()
        assert result != CombatResult.DRAW
