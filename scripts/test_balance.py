"""Script: N combates por dificuldade, report win/loss ratio.

Target: 60-80% win rate em medium encounters.
"""

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
from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty
from src.dungeon.encounters.encounter_factory import EncounterFactory
from src.dungeon.encounters.encounter_template_loader import (
    load_templates_by_difficulty,
)
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates

_EMPTY_THRESHOLDS = ThresholdCalculator({})
_COMBATS_PER_TEMPLATE = 50


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


def _run_combats(
    enc_factory: EncounterFactory,
    template,
    n: int,
) -> dict[str, int]:
    """Roda N combates e retorna contagem de resultados."""
    counts = {"VICTORY": 0, "DEFEAT": 0, "DRAW": 0}
    for i in range(n):
        party = _make_party()
        encounter = enc_factory.create(template, rng=Random(i))
        engine = CombatEngine(
            party, list(encounter.enemies), encounter.handler,
        )
        result = engine.run_combat()
        if result == CombatResult.PARTY_VICTORY:
            counts["VICTORY"] += 1
        elif result == CombatResult.PARTY_DEFEAT:
            counts["DEFEAT"] += 1
        else:
            counts["DRAW"] += 1
    return counts


def main() -> None:
    enc_factory = _make_encounter_factory()

    print("=" * 70)
    print(f"  BALANCE REPORT — {_COMBATS_PER_TEMPLATE} combats per template")
    print("=" * 70)

    for difficulty in EncounterDifficulty:
        templates = load_templates_by_difficulty(difficulty)
        if not templates:
            continue
        print(f"\n  {difficulty.name}:")
        for tid, template in templates.items():
            counts = _run_combats(enc_factory, template, _COMBATS_PER_TEMPLATE)
            total = sum(counts.values())
            win_pct = counts["VICTORY"] / total * 100 if total else 0
            draw_pct = counts["DRAW"] / total * 100 if total else 0
            bar = _bar(win_pct)
            print(
                f"    {tid:25s} | "
                f"Win {counts['VICTORY']:3d}/{total} ({win_pct:5.1f}%) "
                f"| Draw {counts['DRAW']:2d} ({draw_pct:4.1f}%) "
                f"| {bar}",
            )

    print("\n" + "=" * 70)
    print("  Target: 60-80% win rate em MEDIUM encounters")
    print("=" * 70)


def _bar(pct: float) -> str:
    filled = int(pct / 5)
    return "[" + "#" * filled + "." * (20 - filled) + "]"


if __name__ == "__main__":
    main()
