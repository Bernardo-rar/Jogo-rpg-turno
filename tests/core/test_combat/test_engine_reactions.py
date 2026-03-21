"""Tests for CombatEngine integration with ReactionManager."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatEvent,
    EventType,
    TurnContext,
)
from src.core.combat.damage import DamageResult
from src.core.combat.reaction_manager import ReactionManager
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


def _make_bar(*skills: Skill) -> SkillBar:
    slot = SpellSlot(max_cost=20, skills=skills)
    return SkillBar(slots=(slot,))


class AttackFirstEnemyHandler:
    """Ataca o primeiro inimigo vivo com 10 de dano."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        targets = [e for e in context.enemies if e.is_alive]
        if not targets:
            return []
        context.action_economy.use(ActionType.ACTION)
        target = targets[0]
        target.take_damage(10)
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=target.name,
            damage=DamageResult(
                raw_damage=10, defense_value=0,
                is_critical=False, final_damage=10,
            ),
        )]


class TestEngineWithReactions:
    def test_engine_accepts_reaction_manager(self) -> None:
        hero = _build_char("Hero")
        enemy = _build_char("Enemy")
        manager = ReactionManager()
        engine = CombatEngine(
            party=[hero], enemies=[enemy],
            turn_handler=AttackFirstEnemyHandler(),
            reaction_manager=manager,
        )
        assert engine is not None

    def test_engine_works_without_reaction_manager(self) -> None:
        hero = _build_char("Hero")
        enemy = _build_char("Enemy")
        engine = CombatEngine(
            party=[hero], enemies=[enemy],
            turn_handler=AttackFirstEnemyHandler(),
        )
        engine.start_round()
        name = engine.get_next_combatant()
        assert name is not None

    def test_passive_reaction_fires_on_damage(self) -> None:
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_parry())
        hero.action_points = _FakeResource(3)

        enemy = _build_char("Enemy")
        manager = ReactionManager()
        engine = CombatEngine(
            party=[hero], enemies=[enemy],
            turn_handler=AttackFirstEnemyHandler(),
            reaction_manager=manager,
        )
        engine.start_round()
        # Enemy ataca Hero → Hero toma dano → Parry dispara
        enemy_name = engine.get_next_combatant()
        step = engine.prepare_turn(enemy_name)
        events = engine._handler.execute_turn(step.context)
        # Agora process reactions antes de resolve
        reaction_events = engine.process_damage_reactions(events)
        all_events = events + reaction_events
        engine.resolve_turn(all_events)

        # Parry deve ter gerado um BUFF event
        buff_events = [e for e in all_events if e.event_type == EventType.BUFF]
        assert len(buff_events) >= 1

    def test_passive_reaction_spends_resource_on_damage(self) -> None:
        resource = _FakeResource(3)
        hero = _build_char("Hero")
        hero._skill_bar = _make_bar(_parry())
        hero.action_points = resource

        enemy = _build_char("Enemy")
        manager = ReactionManager()
        engine = CombatEngine(
            party=[hero], enemies=[enemy],
            turn_handler=AttackFirstEnemyHandler(),
            reaction_manager=manager,
        )
        engine.start_round()
        enemy_name = engine.get_next_combatant()
        step = engine.prepare_turn(enemy_name)
        events = engine._handler.execute_turn(step.context)
        engine.process_damage_reactions(events)

        assert resource.current == 2
