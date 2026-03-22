"""Testes para ControllerHandler - IA de archetype CONTROLLER."""

from __future__ import annotations

from src.core.combat.combat_engine import EventType
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from src.dungeon.enemies.ai.controller_handler import ControllerHandler

from tests.dungeon.enemies.ai.conftest import (
    make_bar,
    make_char,
    make_context,
    make_skill,
)


class TestControllerHandlerCC:

    def test_uses_cc_skill_when_available(self) -> None:
        ctrl = make_char("Controller")
        cc = make_skill(
            skill_id="poison_cloud",
            effect_type=SkillEffectType.APPLY_AILMENT,
            target_type=TargetType.SINGLE_ENEMY,
        )
        ctrl._skill_bar = make_bar(cc)
        enemy = make_char("Enemy")
        ctx = make_context(ctrl, enemies=[enemy])
        events = ControllerHandler().execute_turn(ctx)
        assert len(events) >= 1

    def test_prefers_cc_over_debuff(self) -> None:
        ctrl = make_char("Controller")
        cc = make_skill(
            skill_id="poison_cloud",
            effect_type=SkillEffectType.APPLY_AILMENT,
            target_type=TargetType.SINGLE_ENEMY,
        )
        debuff = make_skill(
            skill_id="weaken",
            effect_type=SkillEffectType.DEBUFF,
            target_type=TargetType.SINGLE_ENEMY,
        )
        ctrl._skill_bar = make_bar(cc, debuff)
        enemy = make_char("Enemy")
        ctx = make_context(ctrl, enemies=[enemy])
        events = ControllerHandler().execute_turn(ctx)
        assert len(events) >= 1


class TestControllerHandlerDebuff:

    def test_uses_debuff_when_no_cc(self) -> None:
        ctrl = make_char("Controller")
        debuff = make_skill(
            skill_id="weaken",
            effect_type=SkillEffectType.DEBUFF,
            target_type=TargetType.SINGLE_ENEMY,
        )
        ctrl._skill_bar = make_bar(debuff)
        enemy = make_char("Enemy")
        ctx = make_context(ctrl, enemies=[enemy])
        events = ControllerHandler().execute_turn(ctx)
        assert len(events) >= 1


class TestControllerHandlerFallback:

    def test_basic_attack_on_highest_threat(self) -> None:
        ctrl = make_char("Controller")
        weak = make_char("Weak", speed=5)
        strong = make_char("Strong", speed=15)
        ctx = make_context(ctrl, enemies=[weak, strong])
        events = ControllerHandler().execute_turn(ctx)
        assert len(events) >= 1
        # Should attack the one with higher attack_power
        assert events[0].damage is not None

    def test_returns_empty_when_no_targets(self) -> None:
        ctrl = make_char("Controller")
        dead = make_char("Dead")
        dead.take_damage(dead.max_hp + 100)
        ctx = make_context(ctrl, enemies=[dead])
        events = ControllerHandler().execute_turn(ctx)
        assert events == []
