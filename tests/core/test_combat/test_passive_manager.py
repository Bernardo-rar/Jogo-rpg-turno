"""Tests for PassiveManager — auto-fires passive skills on combat events."""

from __future__ import annotations

import pytest

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.passive_manager import PassiveManager
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType


def _make_passive_skill(
    trigger: str,
    stat: ModifiableStat = ModifiableStat.PHYSICAL_ATTACK,
    power: int = 10,
    duration: int = 2,
) -> Skill:
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
                base_power=power,
                stat=stat,
                duration=duration,
            ),
        ),
        reaction_trigger=trigger,
        reaction_mode="passive",
    )


def _attach_skill_bar(character, *skills: Skill) -> None:
    """Anexa SkillBar com as skills dadas ao personagem."""
    slot = SpellSlot(max_cost=999, skills=tuple(skills))
    character._skill_bar = SkillBar(slots=(slot,))


@pytest.fixture
def manager() -> PassiveManager:
    return PassiveManager()


class TestFireOnRoundStart:
    def test_applies_buff(self, make_char, manager) -> None:
        char = make_char("Warrior")
        skill = _make_passive_skill("on_round_start")
        _attach_skill_bar(char, skill)

        events = manager.fire_on_round_start([char], round_number=1)

        assert len(events) == 1
        assert events[0].event_type == EventType.BUFF
        assert events[0].target_name == "Warrior"


class TestFireOnKill:
    def test_applies_buff(self, make_char, manager) -> None:
        killer = make_char("Slayer")
        skill = _make_passive_skill(
            "on_kill", stat=ModifiableStat.PHYSICAL_ATTACK, power=15,
        )
        _attach_skill_bar(killer, skill)

        events = manager.fire_on_kill(killer, round_number=3)

        assert len(events) == 1
        assert events[0].event_type == EventType.BUFF
        assert events[0].actor_name == "Slayer"


class TestFireOnLowHp:
    def test_triggers_below_threshold(self, make_char, manager) -> None:
        char = make_char("Tank")
        skill = _make_passive_skill(
            "on_low_hp", stat=ModifiableStat.PHYSICAL_DEFENSE, power=15,
        )
        _attach_skill_bar(char, skill)
        # Reduz HP para 40% do max
        damage = int(char.max_hp * 0.6)
        char.take_damage(damage)

        events = manager.fire_on_low_hp(char, round_number=2)

        assert len(events) == 1
        assert events[0].event_type == EventType.BUFF

    def test_does_not_trigger_above_threshold(
        self, make_char, manager,
    ) -> None:
        char = make_char("Healthy")
        skill = _make_passive_skill("on_low_hp")
        _attach_skill_bar(char, skill)
        # HP esta em 100%, nao deve disparar
        events = manager.fire_on_low_hp(char, round_number=2)

        assert events == []


class TestFireOnCritical:
    def test_applies_buff(self, make_char, manager) -> None:
        attacker = make_char("Critter")
        skill = _make_passive_skill(
            "on_critical_hit", stat=ModifiableStat.SPEED, power=5,
        )
        _attach_skill_bar(attacker, skill)

        events = manager.fire_on_critical(attacker, round_number=4)

        assert len(events) == 1
        assert events[0].event_type == EventType.BUFF
        assert events[0].actor_name == "Critter"


class TestFireOnAllyDeath:
    def test_applies_buff_to_survivors(
        self, make_char, manager,
    ) -> None:
        survivor = make_char("Avenger")
        skill = _make_passive_skill(
            "on_ally_death", stat=ModifiableStat.PHYSICAL_ATTACK, power=10,
        )
        _attach_skill_bar(survivor, skill)

        events = manager.fire_on_ally_death(
            dead_ally_name="Fallen", party=[survivor], round_number=5,
        )

        assert len(events) == 1
        assert events[0].event_type == EventType.BUFF
        assert events[0].target_name == "Avenger"


class TestPassiveEdgeCases:
    def test_does_not_fire_without_matching_skill(
        self, make_char, manager,
    ) -> None:
        char = make_char("NoPassive")
        # Skill de acao normal, nao passiva
        normal_skill = Skill(
            skill_id="normal", name="Normal Attack",
            mana_cost=5, action_type=ActionType.ACTION,
            target_type=TargetType.SINGLE_ENEMY, slot_cost=4,
            effects=(SkillEffect(
                effect_type=SkillEffectType.DAMAGE, base_power=20,
            ),),
        )
        _attach_skill_bar(char, normal_skill)

        events = manager.fire_on_round_start([char], round_number=1)

        assert events == []

    def test_with_no_skill_bar_returns_empty(
        self, make_char, manager,
    ) -> None:
        char = make_char("Unarmed")
        # Sem skill_bar (default None)
        events = manager.fire_on_round_start([char], round_number=1)

        assert events == []
