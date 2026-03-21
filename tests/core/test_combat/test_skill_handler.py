"""Testes para SkillHandler - executa skills no combate."""

from __future__ import annotations

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.combat_engine import EventType, TurnContext
from src.core.combat.skill_handler import SkillHandler
from src.core.skills.cooldown_tracker import CooldownTracker
from src.core.skills.resource_cost import ResourceCost
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType

from tests.core.test_combat.conftest import _build_char


def _fireball() -> Skill:
    return Skill(
        skill_id="fireball", name="Fireball", mana_cost=10,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        effects=(SkillEffect(effect_type=SkillEffectType.DAMAGE, base_power=20),),
        slot_cost=3,
    )


def _heal() -> Skill:
    return Skill(
        skill_id="heal", name="Heal", mana_cost=5,
        action_type=ActionType.ACTION, target_type=TargetType.SELF,
        effects=(SkillEffect(effect_type=SkillEffectType.HEAL, base_power=15),),
        slot_cost=2, cooldown_turns=2,
    )


def _make_bar(*skills: Skill) -> SkillBar:
    slot = SpellSlot(max_cost=20, skills=skills)
    return SkillBar(slots=(slot,))


def _context(combatant, enemies=None):
    if enemies is None:
        enemies = [_build_char("Enemy")]
    return TurnContext(
        combatant=combatant,
        allies=[combatant],
        enemies=enemies,
        action_economy=ActionEconomy(),
        round_number=1,
    )


class TestSkillHandler:
    def test_no_skill_bar_returns_empty(self) -> None:
        hero = _build_char("Hero")
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert events == []

    def test_no_mana_returns_empty(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_fireball())
        hero.spend_mana(hero.current_mana)
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert events == []

    def test_skill_spends_mana(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_fireball())
        mana_before = hero.current_mana
        handler = SkillHandler()
        handler.execute_turn(_context(hero))
        assert hero.current_mana == mana_before - 10

    def test_skill_uses_action(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_fireball())
        economy = ActionEconomy()
        ctx = TurnContext(
            combatant=hero, allies=[hero],
            enemies=[_build_char("E")],
            action_economy=economy, round_number=1,
        )
        SkillHandler().execute_turn(ctx)
        assert not economy.is_available(ActionType.ACTION)

    def test_skill_damage_creates_event(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_fireball())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1
        assert events[0].damage is not None
        assert events[0].target_name == "Enemy"

    def test_skill_heal_creates_event(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(5)
        hero._skill_bar = _make_bar(_heal())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1
        assert events[0].event_type == EventType.HEAL

    def test_skill_starts_cooldown(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_heal())
        hero.take_damage(5)
        handler = SkillHandler()
        handler.execute_turn(_context(hero))
        tracker = hero.skill_bar.cooldown_tracker
        assert not tracker.is_ready("heal")
        assert tracker.remaining("heal") == 2

    def test_no_action_available_returns_empty(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_fireball())
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        ctx = TurnContext(
            combatant=hero, allies=[hero],
            enemies=[_build_char("E")],
            action_economy=economy, round_number=1,
        )
        events = SkillHandler().execute_turn(ctx)
        assert events == []

    def test_skip_heal_skill_when_all_allies_full_hp(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_heal())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert events == []

    def test_heal_skill_used_when_ally_hurt(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(10)
        hero._skill_bar = _make_bar(_heal())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1
        assert events[0].event_type == EventType.HEAL

    def test_skip_heal_falls_through_to_next_skill(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_heal(), _fireball())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1
        assert events[0].damage is not None


class _FakeResource:
    """Recurso com interface spend/current para testes."""

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


def _power_strike() -> Skill:
    return Skill(
        skill_id="power_strike", name="Power Strike", mana_cost=5,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        effects=(SkillEffect(effect_type=SkillEffectType.DAMAGE, base_power=40),),
        slot_cost=4,
        class_id="fighter",
        resource_costs=(ResourceCost("action_points", 2),),
    )


class TestSkillHandlerResourceCosts:
    def test_skip_skill_when_resource_not_affordable(self) -> None:
        hero = _build_char("Hero")
        hero.action_points = _FakeResource(1)
        hero._skill_bar = _make_bar(_power_strike())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert events == []

    def test_skill_picked_when_resource_affordable(self) -> None:
        hero = _build_char("Hero")
        hero.action_points = _FakeResource(5)
        hero._skill_bar = _make_bar(_power_strike())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1

    def test_skill_spends_class_resource(self) -> None:
        hero = _build_char("Hero")
        resource = _FakeResource(5)
        hero.action_points = resource
        hero._skill_bar = _make_bar(_power_strike())
        handler = SkillHandler()
        handler.execute_turn(_context(hero))
        assert resource.current == 3

    def test_skill_without_resource_costs_works_normally(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_fireball())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1

    def test_fallback_to_cheaper_skill(self) -> None:
        hero = _build_char("Hero")
        hero.action_points = _FakeResource(0)
        hero._skill_bar = _make_bar(_power_strike(), _fireball())
        handler = SkillHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1
        assert events[0].event_type == EventType.DAMAGE
