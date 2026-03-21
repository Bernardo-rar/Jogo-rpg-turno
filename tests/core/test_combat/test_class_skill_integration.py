"""Testes de integracao: skills de classe usam recursos em combate real."""

from __future__ import annotations

import pytest

from src.core.characters.class_resource_snapshot import ResourceDisplayType
from src.core.classes.class_id import ClassId
from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.combat_engine import CombatEvent, EventType, TurnContext
from src.core.combat.skill_handler import SkillHandler
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_loader import load_class_skills
from src.core.skills.spell_slot import SpellSlot

from tests.core.test_combat.conftest import _build_char


class _FakeResource:
    def __init__(self, current: int) -> None:
        self._current = current

    @property
    def current(self) -> int:
        return self._current

    def spend(self, amount: int) -> bool:
        if self._current < amount:
            return False
        self._current -= amount
        return True

    def gain(self, amount: int) -> int:
        self._current += amount
        return amount

    @property
    def limit(self) -> int:
        return 10

    @property
    def max_stacks(self) -> int:
        return 10


def _equip_class_skills(hero, class_id: str, resource_name: str = "", resource_val: int = 10):
    """Equipa todas as skills de uma classe no hero."""
    skills = load_class_skills(class_id)
    all_skills = tuple(skills.values())
    slot = SpellSlot(max_cost=100, skills=all_skills)
    hero._skill_bar = SkillBar(slots=(slot,))
    if resource_name:
        setattr(hero, resource_name, _FakeResource(resource_val))
    return skills


def _context(hero, enemies=None):
    if enemies is None:
        enemies = [_build_char("Enemy")]
    return TurnContext(
        combatant=hero, allies=[hero],
        enemies=enemies,
        action_economy=ActionEconomy(),
        round_number=1,
    )


class TestFighterSkillsIntegration:
    def test_power_strike_spends_ap(self) -> None:
        hero = _build_char("Fighter1")
        _equip_class_skills(hero, "fighter", "action_points", 5)
        resource = hero.action_points

        events = SkillHandler().execute_turn(_context(hero))

        assert len(events) >= 1
        assert resource.current < 5

    def test_no_ap_skips_ap_skills(self) -> None:
        hero = _build_char("Fighter1")
        hero.action_points = _FakeResource(0)
        skills = load_class_skills("fighter")
        # Only equip power_strike (needs AP)
        ps = skills["power_strike"]
        slot = SpellSlot(max_cost=100, skills=(ps,))
        hero._skill_bar = SkillBar(slots=(slot,))

        events = SkillHandler().execute_turn(_context(hero))
        assert events == []

    def test_parry_is_reaction_type(self) -> None:
        skills = load_class_skills("fighter")
        parry = skills["parry"]
        assert parry.action_type == ActionType.REACTION
        assert parry.reaction_mode == "passive"


class TestBarbarianSkillsIntegration:
    def test_reckless_strike_spends_fury(self) -> None:
        hero = _build_char("Barbarian1")
        _equip_class_skills(hero, "barbarian", "fury_bar", 30)
        resource = hero.fury_bar

        events = SkillHandler().execute_turn(_context(hero))

        assert len(events) >= 1
        assert resource.current < 30


class TestMageSkillsIntegration:
    def test_fire_bolt_uses_mana_only(self) -> None:
        hero = _build_char("Mage1")
        skills = load_class_skills("mage")
        fb = skills["fire_bolt"]
        slot = SpellSlot(max_cost=100, skills=(fb,))
        hero._skill_bar = SkillBar(slots=(slot,))
        mana_before = hero.current_mana

        events = SkillHandler().execute_turn(_context(hero))

        assert len(events) >= 1
        assert hero.current_mana < mana_before


class TestClericSkillsIntegration:
    def test_divine_smite_spends_holy_power(self) -> None:
        hero = _build_char("Cleric1")
        resource = _FakeResource(3)
        hero.holy_power = resource
        skills = load_class_skills("cleric")
        smite = skills["divine_smite"]
        slot = SpellSlot(max_cost=100, skills=(smite,))
        hero._skill_bar = SkillBar(slots=(slot,))

        events = SkillHandler().execute_turn(_context(hero))

        assert len(events) >= 1
        assert hero.holy_power.current == 2


@pytest.mark.parametrize("class_id", [c.value for c in ClassId])
class TestAllClassSkillsLoad:
    def test_all_skills_parseable(self, class_id: str) -> None:
        skills = load_class_skills(class_id)
        assert len(skills) == 6

    def test_at_least_one_reaction_per_class(self, class_id: str) -> None:
        skills = load_class_skills(class_id)
        reactions = [s for s in skills.values()
                     if s.action_type == ActionType.REACTION]
        assert len(reactions) >= 1, f"{class_id} has no REACTION skill"


class TestResourceSnapshotIntegration:
    def test_fighter_has_resource_snapshots(self) -> None:
        from src.core.classes.fighter.fighter import Fighter
        from src.core.attributes.attributes import Attributes
        from src.core.attributes.attribute_types import AttributeType
        from src.core.characters.character_config import CharacterConfig
        from src.core.characters.class_modifiers import ClassModifiers
        from src.core.attributes.threshold_calculator import ThresholdCalculator

        attrs = Attributes()
        for at in AttributeType:
            attrs.set(at, 10)
        mods = ClassModifiers(
            hit_dice=12, vida_mod=0, mod_hp=10,
            mana_multiplier=6,
            mod_atk_physical=10, mod_atk_magical=6,
            mod_def_physical=5, mod_def_magical=3,
            regen_hp_mod=5, regen_mana_mod=3,
        )
        config = CharacterConfig(
            class_modifiers=mods,
            threshold_calculator=ThresholdCalculator({}),
        )
        fighter = Fighter("TestFighter", attrs, config)
        snaps = fighter.get_resource_snapshots()

        assert len(snaps) >= 1
        ap_snap = snaps[0]
        assert ap_snap.name == "AP"
        assert ap_snap.display_type == ResourceDisplayType.COUNTER
