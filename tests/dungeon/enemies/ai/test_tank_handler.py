"""Testes para TankHandler - IA de archetype TANK."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.characters.position import Position
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from src.dungeon.enemies.ai.tank_handler import TankHandler

from tests.dungeon.enemies.ai.conftest import (
    make_bar,
    make_char,
    make_context,
    make_skill,
)


class TestTankHandlerOpeningBuff:

    def test_buffs_on_round_one(self) -> None:
        tank = make_char("Tank")
        buff = make_skill(
            skill_id="taunt",
            effect_type=SkillEffectType.BUFF,
            target_type=TargetType.SELF,
        )
        tank._skill_bar = make_bar(buff)
        enemy = make_char("Enemy")
        ctx = make_context(tank, enemies=[enemy], round_number=1)
        events = TankHandler().execute_turn(ctx)
        assert len(events) >= 1

    def test_no_buff_after_round_one(self) -> None:
        tank = make_char("Tank")
        ally = make_char("Ally")
        buff = make_skill(
            skill_id="taunt",
            effect_type=SkillEffectType.BUFF,
            target_type=TargetType.SELF,
        )
        tank._skill_bar = make_bar(buff)
        enemy = make_char("Enemy")
        hp_before = enemy.current_hp
        ctx = make_context(tank, allies=[tank, ally], enemies=[enemy], round_number=2)
        events = TankHandler().execute_turn(ctx)
        # Should basic attack instead of buffing
        assert len(events) >= 1
        assert enemy.current_hp < hp_before


class TestTankHandlerAttack:

    def test_attacks_front_line(self) -> None:
        tank = make_char("Tank")
        front = make_char("Front", position=Position.FRONT)
        back = make_char("Back", position=Position.BACK)
        ctx = make_context(tank, enemies=[front, back], round_number=2)
        events = TankHandler().execute_turn(ctx)
        assert events[0].target_name == "Front"

    def test_attacks_back_if_no_front(self) -> None:
        tank = make_char("Tank")
        back = make_char("Back", position=Position.BACK)
        ctx = make_context(tank, enemies=[back], round_number=2)
        events = TankHandler().execute_turn(ctx)
        assert len(events) >= 1
        assert events[0].target_name == "Back"


class TestTankHandlerEnrage:

    def test_enrages_when_last_alive(self) -> None:
        tank = make_char("Tank")
        dead_ally = make_char("DeadAlly")
        dead_ally.take_damage(dead_ally.max_hp + 100)
        enrage = make_skill(
            skill_id="enrage",
            action_type=ActionType.BONUS_ACTION,
            effect_type=SkillEffectType.BUFF,
            target_type=TargetType.SELF,
        )
        tank._skill_bar = make_bar(enrage)
        enemy = make_char("Enemy")
        ctx = make_context(
            tank,
            allies=[tank, dead_ally],
            enemies=[enemy],
            round_number=3,
        )
        events = TankHandler().execute_turn(ctx)
        # Should enrage (bonus) AND attack (action)
        assert len(events) >= 2

    def test_no_enrage_with_alive_allies(self) -> None:
        tank = make_char("Tank")
        ally = make_char("Ally")
        enrage = make_skill(
            skill_id="enrage",
            effect_type=SkillEffectType.BUFF,
            target_type=TargetType.SELF,
        )
        tank._skill_bar = make_bar(enrage)
        enemy = make_char("Enemy")
        ctx = make_context(
            tank,
            allies=[tank, ally],
            enemies=[enemy],
            round_number=3,
        )
        events = TankHandler().execute_turn(ctx)
        # Should just attack, no enrage
        assert len(events) == 1
        assert events[0].damage is not None
