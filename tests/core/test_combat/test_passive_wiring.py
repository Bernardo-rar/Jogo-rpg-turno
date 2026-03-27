"""Tests for PassiveManager wiring into CombatEngine."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatEvent,
    EventType,
    TurnContext,
)
from src.core.combat.damage import DamageResult
from src.core.combat.passive_manager import PassiveManager
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType

from tests.core.test_combat.conftest import _build_char


class _DoNothingHandler:
    """Handler que nao faz nada."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        return []


def _make_passive_skill(trigger: str) -> Skill:
    """Cria skill passiva de teste com trigger configuravel."""
    return Skill(
        skill_id=f"test_{trigger}",
        name=f"Test {trigger}",
        mana_cost=0,
        action_type=ActionType.PASSIVE,
        target_type=TargetType.SELF,
        slot_cost=0,
        effects=(
            SkillEffect(
                effect_type=SkillEffectType.BUFF,
                base_power=5,
                stat=ModifiableStat.PHYSICAL_ATTACK,
                duration=2,
            ),
        ),
        reaction_trigger=trigger,
        reaction_mode="passive",
    )


def _attach_passive(character, trigger: str) -> None:
    """Anexa skill passiva com trigger ao personagem."""
    skill = _make_passive_skill(trigger)
    slot = SpellSlot(max_cost=999, skills=(skill,))
    character._skill_bar = SkillBar(slots=(slot,))


def _make_engine(
    party, enemies, passive_manager=None,
) -> CombatEngine:
    """Cria engine com handler noop e passive_manager opcional."""
    return CombatEngine(
        party=party,
        enemies=enemies,
        turn_handler=_DoNothingHandler(),
        passive_manager=passive_manager,
    )


class TestRoundStartFiresPassives:
    def test_round_start_fires_passives(self) -> None:
        hero = _build_char("Hero")
        _attach_passive(hero, "on_round_start")
        engine = _make_engine(
            [hero], [_build_char("Goblin")],
            passive_manager=PassiveManager(),
        )

        engine.start_round()

        passive_events = [
            e for e in engine.events
            if e.event_type == EventType.BUFF
        ]
        assert len(passive_events) == 1
        assert passive_events[0].target_name == "Hero"


class TestNoPassiveManagerNoEvents:
    def test_no_passive_manager_no_events(self) -> None:
        hero = _build_char("Hero2")
        _attach_passive(hero, "on_round_start")
        engine = _make_engine([hero], [_build_char("Goblin2")])

        engine.start_round()

        assert len(engine.events) == 0


class TestKillFiresOnKillPassive:
    def test_kill_fires_on_kill_passive(self) -> None:
        hero = _build_char("Killer")
        _attach_passive(hero, "on_kill")
        enemy = _build_char("Victim")
        engine = _make_engine(
            [hero], [enemy],
            passive_manager=PassiveManager(),
        )
        engine.start_round()
        # Mata o inimigo via dano direto
        enemy.take_damage(enemy.current_hp)
        kill_event = CombatEvent(
            round_number=1,
            actor_name="Killer",
            target_name="Victim",
            damage=DamageResult(
                raw_damage=999, defense_value=0,
                is_critical=False, final_damage=999,
            ),
        )

        engine.resolve_turn([kill_event])

        on_kill_events = [
            e for e in engine.events
            if e.event_type == EventType.BUFF
            and e.target_name == "Killer"
        ]
        assert len(on_kill_events) == 1


class TestLowHpFiresPassive:
    def test_low_hp_fires_passive(self) -> None:
        hero = _build_char("Tank")
        enemy = _build_char("Attacker")
        _attach_passive(hero, "on_low_hp")
        engine = _make_engine(
            [hero], [enemy],
            passive_manager=PassiveManager(),
        )
        engine.start_round()
        # Reduz HP do hero para abaixo de 50%
        damage_amount = int(hero.max_hp * 0.6)
        hero.take_damage(damage_amount)
        damage_event = CombatEvent(
            round_number=1,
            actor_name="Attacker",
            target_name="Tank",
            damage=DamageResult(
                raw_damage=damage_amount, defense_value=0,
                is_critical=False, final_damage=damage_amount,
            ),
        )

        engine.resolve_turn([damage_event])

        low_hp_events = [
            e for e in engine.events
            if e.event_type == EventType.BUFF
            and e.target_name == "Tank"
        ]
        assert len(low_hp_events) == 1


class TestCriticalFiresPassive:
    def test_critical_fires_passive(self) -> None:
        hero = _build_char("Critter")
        enemy = _build_char("Target")
        _attach_passive(hero, "on_critical_hit")
        engine = _make_engine(
            [hero], [enemy],
            passive_manager=PassiveManager(),
        )
        engine.start_round()
        crit_event = CombatEvent(
            round_number=1,
            actor_name="Critter",
            target_name="Target",
            damage=DamageResult(
                raw_damage=50, defense_value=10,
                is_critical=True, final_damage=40,
            ),
        )

        engine.resolve_turn([crit_event])

        crit_passive_events = [
            e for e in engine.events
            if e.event_type == EventType.BUFF
            and e.target_name == "Critter"
        ]
        assert len(crit_passive_events) == 1
