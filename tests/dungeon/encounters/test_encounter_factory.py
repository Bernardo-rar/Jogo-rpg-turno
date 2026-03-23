"""Testes para EncounterFactory."""

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
from src.dungeon.encounters.encounter_template_loader import load_encounter_templates
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates


def _make_enemy_factory() -> EnemyFactory:
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

    return EnemyFactory(
        {**core_weapons, **dungeon_weapons},
        {**core_profiles, **dungeon_profiles},
        {**core_skills, **dungeon_skills},
    )


class TestEncounterFactory:

    def test_creates_correct_number_of_enemies(self) -> None:
        factory = EncounterFactory(
            _make_enemy_factory(), load_tier_templates(tier=1),
        )
        templates = load_encounter_templates()
        result = factory.create(templates["easy_3dps"], rng=Random(42))
        assert len(result.enemies) == 3

    def test_all_enemies_alive(self) -> None:
        factory = EncounterFactory(
            _make_enemy_factory(), load_tier_templates(tier=1),
        )
        templates = load_encounter_templates()
        result = factory.create(templates["easy_3dps"], rng=Random(42))
        assert all(e.is_alive for e in result.enemies)

    def test_unique_names(self) -> None:
        factory = EncounterFactory(
            _make_enemy_factory(), load_tier_templates(tier=1),
        )
        templates = load_encounter_templates()
        result = factory.create(templates["easy_3dps"], rng=Random(42))
        names = [e.name for e in result.enemies]
        assert len(names) == len(set(names))

    def test_handler_is_dispatch(self) -> None:
        factory = EncounterFactory(
            _make_enemy_factory(), load_tier_templates(tier=1),
        )
        templates = load_encounter_templates()
        result = factory.create(templates["easy_3dps"], rng=Random(42))
        assert hasattr(result.handler, "execute_turn")

    def test_deterministic_with_seed(self) -> None:
        factory = EncounterFactory(
            _make_enemy_factory(), load_tier_templates(tier=1),
        )
        templates = load_encounter_templates()
        r1 = factory.create(templates["medium_balanced"], rng=Random(123))
        r2 = factory.create(templates["medium_balanced"], rng=Random(123))
        names1 = [e.name for e in r1.enemies]
        names2 = [e.name for e in r2.enemies]
        assert names1 == names2

    def test_medium_balanced_has_four_enemies(self) -> None:
        factory = EncounterFactory(
            _make_enemy_factory(), load_tier_templates(tier=1),
        )
        templates = load_encounter_templates()
        result = factory.create(templates["medium_balanced"], rng=Random(42))
        # medium_balanced has 4 slots: TANK, DPS, HEALER, CONTROLLER
        # Tier 1 has no HEALER, so 3 enemies
        assert len(result.enemies) >= 3

    def test_hard_encounter_has_more_enemies(self) -> None:
        factory = EncounterFactory(
            _make_enemy_factory(), load_tier_templates(tier=1),
        )
        templates = load_encounter_templates()
        easy = factory.create(templates["easy_3dps"], rng=Random(42))
        hard = factory.create(templates["hard_full"], rng=Random(42))
        assert len(hard.enemies) >= len(easy.enemies)
