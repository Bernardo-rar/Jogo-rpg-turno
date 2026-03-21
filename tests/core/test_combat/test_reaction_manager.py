"""Tests for ReactionManager — gerencia reacoes preparadas e passivas."""

from __future__ import annotations

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.reaction_manager import ReactionManager
from src.core.combat.reaction_system import ReactionMode, ReactionTrigger
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.skills.resource_cost import ResourceCost
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType

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


def _parry() -> Skill:
    return Skill(
        skill_id="parry", name="Parry", mana_cost=0,
        action_type=ActionType.REACTION, target_type=TargetType.SELF,
        effects=(
            SkillEffect(effect_type=SkillEffectType.BUFF, base_power=15,
                        stat=ModifiableStat.PHYSICAL_DEFENSE, duration=1),
        ),
        slot_cost=3, class_id="fighter",
        resource_costs=(ResourceCost("action_points", 1),),
        reaction_trigger="on_damage_received",
        reaction_mode="passive",
    )


def _mana_shield() -> Skill:
    return Skill(
        skill_id="mana_shield", name="Mana Shield", mana_cost=0,
        action_type=ActionType.REACTION, target_type=TargetType.SELF,
        effects=(
            SkillEffect(effect_type=SkillEffectType.BUFF, base_power=10,
                        stat=ModifiableStat.MAGICAL_DEFENSE, duration=1),
        ),
        slot_cost=3, class_id="mage",
        reaction_trigger="on_damage_received",
        reaction_mode="prepared",
    )


def _make_bar(*skills: Skill) -> SkillBar:
    slot = SpellSlot(max_cost=20, skills=skills)
    return SkillBar(slots=(slot,))


class TestReactionManagerPrepare:
    def test_prepare_reaction(self) -> None:
        manager = ReactionManager()
        skill = _mana_shield()
        manager.prepare_reaction("Mage1", skill)
        assert manager.has_prepared("Mage1") is True

    def test_no_prepared_by_default(self) -> None:
        manager = ReactionManager()
        assert manager.has_prepared("Fighter1") is False

    def test_clear_prepared(self) -> None:
        manager = ReactionManager()
        manager.prepare_reaction("Mage1", _mana_shield())
        manager.clear_prepared("Mage1")
        assert manager.has_prepared("Mage1") is False


class TestReactionManagerPassive:
    def test_find_passive_reactions_from_skill_bar(self) -> None:
        hero = _build_char("Fighter1")
        hero._skill_bar = _make_bar(_parry())
        manager = ReactionManager()
        passives = manager.get_passive_reactions(hero)
        assert len(passives) == 1
        assert passives[0].skill_id == "parry"

    def test_no_passive_when_no_skill_bar(self) -> None:
        hero = _build_char("Hero")
        manager = ReactionManager()
        passives = manager.get_passive_reactions(hero)
        assert passives == []

    def test_prepared_skills_not_in_passive_list(self) -> None:
        hero = _build_char("Mage1")
        hero._skill_bar = _make_bar(_mana_shield())
        manager = ReactionManager()
        passives = manager.get_passive_reactions(hero)
        assert passives == []


class TestReactionManagerCheckTrigger:
    def test_passive_fires_on_matching_trigger(self) -> None:
        hero = _build_char("Fighter1")
        hero._skill_bar = _make_bar(_parry())
        hero.action_points = _FakeResource(3)
        economy = ActionEconomy()
        manager = ReactionManager()

        events = manager.check_trigger(
            trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
            target=hero,
            economy=economy,
            round_number=1,
        )
        assert len(events) >= 1

    def test_passive_consumes_reaction_action(self) -> None:
        hero = _build_char("Fighter1")
        hero._skill_bar = _make_bar(_parry())
        hero.action_points = _FakeResource(3)
        economy = ActionEconomy()
        manager = ReactionManager()

        manager.check_trigger(
            trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
            target=hero,
            economy=economy,
            round_number=1,
        )
        assert not economy.is_available(ActionType.REACTION)

    def test_passive_spends_resource(self) -> None:
        resource = _FakeResource(3)
        hero = _build_char("Fighter1")
        hero._skill_bar = _make_bar(_parry())
        hero.action_points = resource
        economy = ActionEconomy()
        manager = ReactionManager()

        manager.check_trigger(
            trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
            target=hero,
            economy=economy,
            round_number=1,
        )
        assert resource.current == 2

    def test_passive_not_fired_when_resource_insufficient(self) -> None:
        hero = _build_char("Fighter1")
        hero._skill_bar = _make_bar(_parry())
        hero.action_points = _FakeResource(0)
        economy = ActionEconomy()
        manager = ReactionManager()

        events = manager.check_trigger(
            trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
            target=hero,
            economy=economy,
            round_number=1,
        )
        assert events == []

    def test_passive_not_fired_when_reaction_used(self) -> None:
        hero = _build_char("Fighter1")
        hero._skill_bar = _make_bar(_parry())
        hero.action_points = _FakeResource(5)
        economy = ActionEconomy()
        economy.use(ActionType.REACTION)
        manager = ReactionManager()

        events = manager.check_trigger(
            trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
            target=hero,
            economy=economy,
            round_number=1,
        )
        assert events == []

    def test_prepared_fires_on_matching_trigger(self) -> None:
        hero = _build_char("Mage1")
        economy = ActionEconomy()
        manager = ReactionManager()
        manager.prepare_reaction("Mage1", _mana_shield())

        events = manager.check_trigger(
            trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
            target=hero,
            economy=economy,
            round_number=1,
        )
        assert len(events) >= 1

    def test_no_trigger_on_wrong_event(self) -> None:
        hero = _build_char("Fighter1")
        hero._skill_bar = _make_bar(_parry())
        hero.action_points = _FakeResource(5)
        economy = ActionEconomy()
        manager = ReactionManager()

        events = manager.check_trigger(
            trigger=ReactionTrigger.ON_ENEMY_CAST,
            target=hero,
            economy=economy,
            round_number=1,
        )
        assert events == []
