"""Integration test: passive skills loaded from JSON fire correctly."""

from __future__ import annotations

import pytest

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import EventType
from src.core.combat.passive_manager import PassiveManager
from src.core.skills.skill_loader import load_class_skills
from src.core.skills.skill_bar import SkillBar
from src.core.skills.spell_slot import SpellSlot


def _attach_skill_bar_from_json(character, class_id: str) -> None:
    """Carrega skills do JSON e anexa ao personagem."""
    skills = load_class_skills(class_id)
    all_skills = tuple(skills.values())
    slot = SpellSlot(max_cost=999, skills=all_skills)
    character._skill_bar = SkillBar(slots=(slot,))


class TestPassiveSkillLoadedFromJsonFiresCorrectly:
    def test_fighter_iron_will_fires_on_low_hp(
        self, make_char,
    ) -> None:
        fighter = make_char("Fighter1")
        _attach_skill_bar_from_json(fighter, "fighter")
        damage = int(fighter.max_hp * 0.6)
        fighter.take_damage(damage)

        manager = PassiveManager()
        events = manager.fire_on_low_hp(fighter, round_number=1)

        buff_events = [e for e in events if e.event_type == EventType.BUFF]
        assert len(buff_events) >= 1
        assert buff_events[0].target_name == "Fighter1"

    def test_barbarian_blood_frenzy_passive_fires_on_low_hp(
        self, make_char,
    ) -> None:
        barb = make_char("Barbarian1")
        _attach_skill_bar_from_json(barb, "barbarian")
        damage = int(barb.max_hp * 0.7)
        barb.take_damage(damage)

        manager = PassiveManager()
        events = manager.fire_on_low_hp(barb, round_number=2)

        buff_events = [e for e in events if e.event_type == EventType.BUFF]
        assert len(buff_events) >= 1
        assert buff_events[0].target_name == "Barbarian1"

    def test_rogue_shadow_speed_fires_on_critical(
        self, make_char,
    ) -> None:
        rogue = make_char("Rogue1")
        _attach_skill_bar_from_json(rogue, "rogue")

        manager = PassiveManager()
        events = manager.fire_on_critical(rogue, round_number=3)

        buff_events = [e for e in events if e.event_type == EventType.BUFF]
        assert len(buff_events) >= 1
        assert buff_events[0].actor_name == "Rogue1"

    def test_passive_skill_has_correct_action_type(self) -> None:
        skills = load_class_skills("fighter")
        iron_will = skills["iron_will"]
        assert iron_will.action_type == ActionType.PASSIVE
        assert iron_will.reaction_trigger == "on_low_hp"
        assert iron_will.reaction_mode == "passive"

    def test_passive_skill_does_not_fire_above_hp_threshold(
        self, make_char,
    ) -> None:
        fighter = make_char("HealthyFighter")
        _attach_skill_bar_from_json(fighter, "fighter")

        manager = PassiveManager()
        events = manager.fire_on_low_hp(fighter, round_number=1)

        assert events == []
