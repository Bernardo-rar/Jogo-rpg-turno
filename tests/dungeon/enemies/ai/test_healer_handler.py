"""Testes para HealerHandler - IA de archetype HEALER."""

from __future__ import annotations

from src.core.combat.combat_engine import EventType
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from src.dungeon.enemies.ai.healer_handler import HealerHandler

from tests.dungeon.enemies.ai.conftest import (
    make_bar,
    make_char,
    make_context,
    make_skill,
)


class TestHealerHandlerHeal:

    def test_heals_hurt_ally(self) -> None:
        healer = make_char("Healer")
        hurt_ally = make_char("Hurt")
        hurt_ally.take_damage(int(hurt_ally.max_hp * 0.5))
        heal = make_skill(
            skill_id="cure",
            effect_type=SkillEffectType.HEAL,
            target_type=TargetType.SINGLE_ALLY,
            base_power=20,
        )
        healer._skill_bar = make_bar(heal)
        enemy = make_char("Enemy")
        ctx = make_context(
            healer,
            allies=[healer, hurt_ally],
            enemies=[enemy],
        )
        events = HealerHandler().execute_turn(ctx)
        assert len(events) >= 1
        assert events[0].event_type == EventType.HEAL

    def test_no_heal_when_allies_healthy(self) -> None:
        healer = make_char("Healer")
        ally = make_char("Healthy")
        heal = make_skill(
            skill_id="cure",
            effect_type=SkillEffectType.HEAL,
            target_type=TargetType.SINGLE_ALLY,
        )
        healer._skill_bar = make_bar(heal)
        enemy = make_char("Enemy")
        ctx = make_context(
            healer,
            allies=[healer, ally],
            enemies=[enemy],
        )
        events = HealerHandler().execute_turn(ctx)
        # Should NOT heal (all healthy), should attack or buff
        assert all(e.event_type != EventType.HEAL for e in events)


class TestHealerHandlerBuff:

    def test_buffs_when_all_healthy(self) -> None:
        healer = make_char("Healer")
        ally = make_char("Healthy")
        buff = make_skill(
            skill_id="bless",
            effect_type=SkillEffectType.BUFF,
            target_type=TargetType.ALL_ALLIES,
        )
        healer._skill_bar = make_bar(buff)
        enemy = make_char("Enemy")
        ctx = make_context(
            healer,
            allies=[healer, ally],
            enemies=[enemy],
        )
        events = HealerHandler().execute_turn(ctx)
        assert len(events) >= 1

    def test_prefers_heal_over_buff(self) -> None:
        healer = make_char("Healer")
        hurt = make_char("Hurt")
        hurt.take_damage(int(hurt.max_hp * 0.5))
        heal = make_skill(
            skill_id="cure",
            effect_type=SkillEffectType.HEAL,
            target_type=TargetType.SINGLE_ALLY,
        )
        buff = make_skill(
            skill_id="bless",
            effect_type=SkillEffectType.BUFF,
            target_type=TargetType.ALL_ALLIES,
        )
        healer._skill_bar = make_bar(heal, buff)
        enemy = make_char("Enemy")
        ctx = make_context(
            healer,
            allies=[healer, hurt],
            enemies=[enemy],
        )
        events = HealerHandler().execute_turn(ctx)
        assert events[0].event_type == EventType.HEAL


class TestHealerHandlerFallback:

    def test_attacks_when_no_skills(self) -> None:
        healer = make_char("Healer")
        enemy = make_char("Enemy")
        hp_before = enemy.current_hp
        ctx = make_context(healer, enemies=[enemy])
        events = HealerHandler().execute_turn(ctx)
        assert len(events) >= 1
        assert enemy.current_hp < hp_before

    def test_returns_empty_when_no_targets(self) -> None:
        healer = make_char("Healer")
        dead = make_char("Dead")
        dead.take_damage(dead.max_hp + 100)
        ctx = make_context(healer, enemies=[dead])
        events = HealerHandler().execute_turn(ctx)
        assert events == []
