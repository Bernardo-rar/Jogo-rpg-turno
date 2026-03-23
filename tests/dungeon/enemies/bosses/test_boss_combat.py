"""Testes de integração: bosses em combate real."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.combat.combat_engine import CombatEngine, CombatResult
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.elements.elemental_profile import ElementalProfile, load_profiles
from src.core.items.weapon import Weapon
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_skills
from src.dungeon.enemies.bosses.boss_factory import BossFactory
from src.dungeon.enemies.bosses.boss_loader import load_all_bosses
from src.dungeon.enemies.bosses.boss_registry import register_all_bosses

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


def _make_catalogs() -> tuple[dict, dict, dict]:
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
            resistances={__import__("src.core.elements.element_type", fromlist=["ElementType"]).ElementType[k]: v for k, v in r.items()},
        )
        for name, r in raw_dp.items()
    }

    core_skills = load_skills()
    raw_bs = json.loads(
        resolve_data_path("data/dungeon/enemies/skills/boss_skills.json")
        .read_text(encoding="utf-8"),
    )
    boss_skills = {
        sid: Skill.from_dict(sid, data) for sid, data in raw_bs.items()
    }

    weapons = {**core_weapons, **dungeon_weapons}
    profiles = {**core_profiles, **dungeon_profiles}
    skills = {**core_skills, **boss_skills}
    return weapons, profiles, skills


def _setup() -> BossFactory:
    register_all_bosses()
    weapons, profiles, skills = _make_catalogs()
    return BossFactory(weapons, profiles, skills)


class TestBossCombat:

    def test_goblin_king_combat_runs(self) -> None:
        factory = _setup()
        bosses = load_all_bosses()
        result = factory.create(bosses["goblin_king"])
        party = _make_party()
        handler = DispatchTurnHandler(
            {result.character.name: result.handler},
            BasicAttackHandler(),
        )
        engine = CombatEngine(party, [result.character], handler)
        combat_result = engine.run_combat()
        assert combat_result in (
            CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT,
        )

    def test_ancient_golem_combat_runs(self) -> None:
        factory = _setup()
        bosses = load_all_bosses()
        result = factory.create(bosses["ancient_golem"])
        party = _make_party()
        handler = DispatchTurnHandler(
            {result.character.name: result.handler},
            BasicAttackHandler(),
        )
        engine = CombatEngine(party, [result.character], handler)
        combat_result = engine.run_combat()
        assert combat_result in (
            CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT,
        )

    def test_lich_lord_combat_runs(self) -> None:
        factory = _setup()
        bosses = load_all_bosses()
        result = factory.create(bosses["lich_lord"])
        party = _make_party()
        handler = DispatchTurnHandler(
            {result.character.name: result.handler},
            BasicAttackHandler(),
        )
        engine = CombatEngine(party, [result.character], handler)
        combat_result = engine.run_combat()
        assert combat_result in (
            CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT,
        )

    def test_goblin_king_changes_phase(self) -> None:
        factory = _setup()
        bosses = load_all_bosses()
        result = factory.create(bosses["goblin_king"])
        boss = result.character
        assert result.handler.current_phase == 1
        # Dano pra abaixar HP pra < 50%
        damage = int(boss.max_hp * 0.55)
        boss.take_damage(damage)
        party = _make_party()
        handler = DispatchTurnHandler(
            {boss.name: result.handler},
            BasicAttackHandler(),
        )
        engine = CombatEngine(party, [boss], handler)
        engine.run_round()
        assert result.handler.current_phase == 2

    def test_boss_produces_events(self) -> None:
        factory = _setup()
        bosses = load_all_bosses()
        result = factory.create(bosses["goblin_king"])
        party = _make_party()
        handler = DispatchTurnHandler(
            {result.character.name: result.handler},
            BasicAttackHandler(),
        )
        engine = CombatEngine(party, [result.character], handler)
        engine.run_combat()
        assert len(engine.events) > 0
