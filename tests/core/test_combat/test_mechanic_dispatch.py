"""Testes para _MECHANIC_DISPATCH — skills TRIGGER_CLASS_MECHANIC."""

from __future__ import annotations

from src.core.combat.skill_effect_applier import (
    _MECHANIC_DISPATCH,
    apply_skill_effect,
)
from src.core.classes.fighter.stance import Stance
from src.core.items.weapon_loader import load_weapons
from src.core.classes.class_id import ClassId
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.dungeon.run.party_factory import PartyFactory

_WEAPONS = load_weapons()
_FACTORY = PartyFactory(_WEAPONS)


def _make_effect(mechanic_id: str) -> SkillEffect:
    return SkillEffect(
        effect_type=SkillEffectType.TRIGGER_CLASS_MECHANIC,
        base_power=0,
        mechanic_id=mechanic_id,
    )


class TestMechanicDispatchRegistered:
    def test_stance_offensive_registered(self) -> None:
        assert "change_stance_offensive" in _MECHANIC_DISPATCH

    def test_stance_defensive_registered(self) -> None:
        assert "change_stance_defensive" in _MECHANIC_DISPATCH

    def test_stance_normal_registered(self) -> None:
        assert "change_stance_normal" in _MECHANIC_DISPATCH

    def test_reckless_stance_registered(self) -> None:
        assert "activate_reckless_stance" in _MECHANIC_DISPATCH


class TestFighterStanceMechanic:
    def test_change_to_offensive(self) -> None:
        fighter = _FACTORY.create(ClassId.FIGHTER, "F")
        assert fighter.stance == Stance.NORMAL
        effect = _make_effect("change_stance_offensive")
        apply_skill_effect(effect, [fighter], 1, fighter)
        assert fighter.stance == Stance.OFFENSIVE

    def test_change_to_defensive(self) -> None:
        fighter = _FACTORY.create(ClassId.FIGHTER, "F")
        effect = _make_effect("change_stance_defensive")
        apply_skill_effect(effect, [fighter], 1, fighter)
        assert fighter.stance == Stance.DEFENSIVE

    def test_change_back_to_normal(self) -> None:
        fighter = _FACTORY.create(ClassId.FIGHTER, "F")
        fighter.change_stance(Stance.OFFENSIVE)
        effect = _make_effect("change_stance_normal")
        apply_skill_effect(effect, [fighter], 1, fighter)
        assert fighter.stance == Stance.NORMAL

    def test_generates_combat_event(self) -> None:
        fighter = _FACTORY.create(ClassId.FIGHTER, "F")
        effect = _make_effect("change_stance_offensive")
        events = apply_skill_effect(effect, [fighter], 1, fighter)
        assert len(events) == 1
        assert events[0].actor_name == "F"


class TestBarbarianRecklessMechanic:
    def test_toggle_on(self) -> None:
        barb = _FACTORY.create(ClassId.BARBARIAN, "B")
        assert not barb.is_reckless
        effect = _make_effect("activate_reckless_stance")
        apply_skill_effect(effect, [barb], 1, barb)
        assert barb.is_reckless

    def test_toggle_off(self) -> None:
        barb = _FACTORY.create(ClassId.BARBARIAN, "B")
        barb.toggle_reckless()
        assert barb.is_reckless
        effect = _make_effect("activate_reckless_stance")
        apply_skill_effect(effect, [barb], 1, barb)
        assert not barb.is_reckless

    def test_non_barbarian_ignores_reckless(self) -> None:
        fighter = _FACTORY.create(ClassId.FIGHTER, "F")
        effect = _make_effect("activate_reckless_stance")
        events = apply_skill_effect(effect, [fighter], 1, fighter)
        assert len(events) == 1
