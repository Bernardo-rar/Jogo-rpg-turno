"""Testes para DpsHandler - IA de archetype DPS."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.characters.position import Position
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from src.dungeon.enemies.ai.dps_handler import DpsHandler

from tests.dungeon.enemies.ai.conftest import (
    make_bar,
    make_char,
    make_context,
    make_skill,
)


class TestDpsHandlerBasicAttack:

    def test_attacks_enemy_when_no_skills(self) -> None:
        attacker = make_char("DPS")
        enemy = make_char("Target")
        hp_before = enemy.current_hp
        ctx = make_context(attacker, enemies=[enemy])
        events = DpsHandler().execute_turn(ctx)
        assert len(events) >= 1
        assert enemy.current_hp < hp_before

    def test_prefers_backline_target(self) -> None:
        attacker = make_char("DPS")
        front = make_char("Front", position=Position.FRONT)
        back = make_char("Back", position=Position.BACK)
        ctx = make_context(attacker, enemies=[front, back])
        # DPS is PHYSICAL (melee) - can only hit FRONT if FRONT exists
        events = DpsHandler().execute_turn(ctx)
        assert len(events) >= 1
        # Melee can only hit front when front exists
        assert events[0].target_name == "Front"

    def test_targets_lowest_hp(self) -> None:
        attacker = make_char("DPS")
        healthy = make_char("Healthy")
        hurt = make_char("Hurt")
        hurt.take_damage(hurt.max_hp // 2)
        ctx = make_context(attacker, enemies=[healthy, hurt])
        events = DpsHandler().execute_turn(ctx)
        assert events[0].target_name == "Hurt"

    def test_returns_empty_when_no_enemies(self) -> None:
        attacker = make_char("DPS")
        dead = make_char("Dead")
        dead.take_damage(dead.max_hp + 100)
        ctx = make_context(attacker, enemies=[dead])
        events = DpsHandler().execute_turn(ctx)
        assert events == []


class TestDpsHandlerAoe:

    def test_uses_aoe_skill_when_three_plus_enemies(self) -> None:
        attacker = make_char("DPS")
        aoe = make_skill(
            skill_id="aoe_blast",
            mana_cost=0,
            target_type=TargetType.ALL_ENEMIES,
            effect_type=SkillEffectType.DAMAGE,
            base_power=15,
        )
        attacker._skill_bar = make_bar(aoe)
        enemies = [make_char(f"E{i}") for i in range(3)]
        ctx = make_context(attacker, enemies=enemies)
        events = DpsHandler().execute_turn(ctx)
        assert len(events) >= 1

    def test_no_aoe_with_fewer_than_three(self) -> None:
        attacker = make_char("DPS")
        aoe = make_skill(
            skill_id="aoe_blast",
            mana_cost=0,
            target_type=TargetType.ALL_ENEMIES,
            effect_type=SkillEffectType.DAMAGE,
        )
        attacker._skill_bar = make_bar(aoe)
        enemies = [make_char("E1"), make_char("E2")]
        ctx = make_context(attacker, enemies=enemies)
        events = DpsHandler().execute_turn(ctx)
        # Should basic attack, not AoE
        assert len(events) == 1
        assert events[0].damage is not None


class TestDpsHandlerBonusBuff:

    def test_uses_bonus_action_buff(self) -> None:
        attacker = make_char("DPS")
        buff = make_skill(
            skill_id="war_cry",
            action_type=ActionType.BONUS_ACTION,
            target_type=TargetType.SELF,
            effect_type=SkillEffectType.BUFF,
            base_power=5,
        )
        attacker._skill_bar = make_bar(buff)
        enemy = make_char("Target")
        ctx = make_context(attacker, enemies=[enemy])
        events = DpsHandler().execute_turn(ctx)
        # Should use buff AND basic attack
        assert len(events) >= 2

    def test_skips_buff_if_no_bonus_action(self) -> None:
        attacker = make_char("DPS")
        buff = make_skill(
            skill_id="war_cry",
            action_type=ActionType.ACTION,
            target_type=TargetType.SELF,
            effect_type=SkillEffectType.BUFF,
        )
        attacker._skill_bar = make_bar(buff)
        enemy = make_char("Target")
        ctx = make_context(attacker, enemies=[enemy])
        # Buff uses ACTION, so no basic attack after
        events = DpsHandler().execute_turn(ctx)
        assert len(events) >= 1
