"""Script: party vs encounters Tier 1 (easy/medium/hard)."""

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
)
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates

_EMPTY_THRESHOLDS = ThresholdCalculator({})


def _attrs(s: int, d: int, c: int, i: int, w: int, ch: int, m: int) -> Attributes:
    a = Attributes()
    for attr_type, val in zip(AttributeType, [s, d, c, i, w, ch, m]):
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


def main() -> None:
    templates = load_encounter_templates()
    enc_factory = _make_encounter_factory()

    target_templates = [
        "easy_3dps", "easy_2dps_tank",
        "medium_tank_2dps", "medium_balanced",
        "hard_double_tank", "hard_full",
    ]

    print("=" * 60)
    print("  TIER 1 ENCOUNTER TEST")
    print("=" * 60)

    for tid in target_templates:
        if tid not in templates:
            print(f"  [SKIP] {tid} — template nao encontrado")
            continue
        party = _make_party()
        encounter = enc_factory.create(templates[tid], rng=Random(42))
        enemy_names = [e.name for e in encounter.enemies]
        engine = CombatEngine(
            party, list(encounter.enemies), encounter.handler,
        )
        result = engine.run_combat()
        status = "VITORIA" if result == CombatResult.PARTY_VICTORY else "DERROTA"
        if result == CombatResult.DRAW:
            status = "EMPATE"
        print(f"  [{status:>7}] {tid:25s} | {len(enemy_names)} enemies | "
              f"{engine.round_number} rounds | enemies: {', '.join(enemy_names)}")

    print("=" * 60)


if __name__ == "__main__":
    main()
