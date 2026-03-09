"""Testes para integracao de cooldown tick no combat engine."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEngine
from src.core.combat.skill_handler import SkillHandler
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType

from tests.core.test_combat.conftest import _build_char


def _heal_skill() -> Skill:
    return Skill(
        skill_id="heal", name="Heal", mana_cost=5,
        action_type=ActionType.ACTION, target_type=TargetType.SELF,
        effects=(SkillEffect(effect_type=SkillEffectType.HEAL, base_power=15),),
        slot_cost=2, cooldown_turns=1,
    )


def _make_bar(*skills: Skill) -> SkillBar:
    slot = SpellSlot(max_cost=20, skills=skills)
    return SkillBar(slots=(slot,))


class TestCooldownIntegration:
    def test_cooldown_ticks_during_round(self) -> None:
        """Cooldown deve reduzir a cada turno do combatente."""
        hero = _build_char("Hero")
        hero.take_damage(5)
        hero._skill_bar = _make_bar(_heal_skill())
        hero.spend_mana(hero.current_mana - 5)
        enemy = _build_char("Enemy", speed=1)
        engine = CombatEngine(
            party=[hero], enemies=[enemy],
            turn_handler=SkillHandler(),
        )
        engine.run_round()
        tracker = hero.skill_bar.cooldown_tracker
        assert tracker.remaining("heal") == 1
        engine.run_round()
        assert tracker.is_ready("heal")

    def test_no_skill_bar_no_error(self) -> None:
        """Personagem sem skill_bar nao causa erro no tick."""
        hero = _build_char("Hero")
        enemy = _build_char("Enemy", speed=1)
        engine = CombatEngine(
            party=[hero], enemies=[enemy],
            turn_handler=SkillHandler(),
        )
        engine.run_round()

    def test_cooldown_ticks_before_handler(self) -> None:
        """Cooldown tick deve acontecer ANTES do handler executar."""
        hero = _build_char("Hero")
        hero.take_damage(5)
        skill = _heal_skill()
        hero._skill_bar = _make_bar(skill)
        hero.skill_bar.cooldown_tracker.start_cooldown("heal", 1)
        enemy = _build_char("Enemy", speed=1)
        engine = CombatEngine(
            party=[hero], enemies=[enemy],
            turn_handler=SkillHandler(),
        )
        engine.run_round()
        assert len(engine.events) == 1
