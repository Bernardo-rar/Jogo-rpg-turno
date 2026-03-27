"""Testes para GRANT_ACTION: ActionEconomy.grant() + SkillHandler integration."""

import json

import pytest

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType


class TestEconomyGrant:
    """Testes unitarios para ActionEconomy.grant()."""

    def test_economy_grant_restores_used_action(self) -> None:
        """grant() deve restaurar uma acao ja consumida."""
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        assert not economy.is_available(ActionType.ACTION)

        economy.grant(ActionType.ACTION)

        assert economy.is_available(ActionType.ACTION)

    def test_economy_grant_noop_when_available(self) -> None:
        """grant() em acao ja disponivel nao causa erro."""
        economy = ActionEconomy()
        assert economy.is_available(ActionType.BONUS_ACTION)

        economy.grant(ActionType.BONUS_ACTION)

        assert economy.is_available(ActionType.BONUS_ACTION)


class TestExecuteSkillGrantAction:
    """Testes de integracao: execute_skill com GRANT_ACTION effects."""

    def test_execute_skill_with_grant_action_restores_economy(
        self, make_char,
    ) -> None:
        """Skill com GRANT_ACTION deve restaurar a acao na economy."""
        from src.core.combat.action_economy import ActionEconomy, ActionType
        from src.core.combat.combat_engine import TurnContext
        from src.core.combat.skill_handler import execute_skill
        from src.core.skills.skill import Skill
        from src.core.skills.target_type import TargetType

        caster = make_char("Caster")
        economy = ActionEconomy()
        # Usar ambas as acoes antes
        economy.use(ActionType.ACTION)
        economy.use(ActionType.BONUS_ACTION)

        skill = Skill(
            skill_id="test_surge",
            name="Test Surge",
            mana_cost=0,
            action_type=ActionType.PASSIVE,
            target_type=TargetType.SELF,
            effects=(
                SkillEffect(
                    effect_type=SkillEffectType.GRANT_ACTION,
                    resource_type="ACTION",
                ),
            ),
            slot_cost=0,
        )
        # grant PASSIVE so it doesn't fail on use()
        economy.grant(ActionType.PASSIVE)
        context = TurnContext(
            combatant=caster,
            allies=[caster],
            enemies=[],
            action_economy=economy,
            round_number=1,
        )

        execute_skill(skill, context)

        assert economy.is_available(ActionType.ACTION)
        assert not economy.is_available(ActionType.BONUS_ACTION)

    def test_grant_action_both_types(self, make_char) -> None:
        """Skill com 2 GRANT_ACTION effects deve restaurar ambas as acoes."""
        from src.core.combat.action_economy import ActionEconomy, ActionType
        from src.core.combat.combat_engine import TurnContext
        from src.core.combat.skill_handler import execute_skill
        from src.core.skills.skill import Skill
        from src.core.skills.target_type import TargetType

        caster = make_char("Caster")
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        economy.use(ActionType.BONUS_ACTION)

        skill = Skill(
            skill_id="full_surge",
            name="Full Surge",
            mana_cost=0,
            action_type=ActionType.PASSIVE,
            target_type=TargetType.SELF,
            effects=(
                SkillEffect(
                    effect_type=SkillEffectType.GRANT_ACTION,
                    resource_type="ACTION",
                ),
                SkillEffect(
                    effect_type=SkillEffectType.GRANT_ACTION,
                    resource_type="BONUS_ACTION",
                ),
            ),
            slot_cost=0,
        )
        economy.grant(ActionType.PASSIVE)
        context = TurnContext(
            combatant=caster,
            allies=[caster],
            enemies=[],
            action_economy=economy,
            round_number=1,
        )

        execute_skill(skill, context)

        assert economy.is_available(ActionType.ACTION)
        assert economy.is_available(ActionType.BONUS_ACTION)


class TestGrantActionFromJson:
    """Testa que fighter.json carrega action_surge com GRANT_ACTION."""

    def test_grant_action_from_json_fighter(self) -> None:
        """action_surge no fighter.json deve usar GRANT_ACTION, nao TRIGGER_CLASS_MECHANIC."""
        from src.core.skills.skill_loader import load_class_skills

        skills = load_class_skills("fighter")
        surge = skills["action_surge"]

        grant_effects = [
            e for e in surge.effects
            if e.effect_type == SkillEffectType.GRANT_ACTION
        ]
        assert len(grant_effects) == 2

        resource_types = {e.resource_type for e in grant_effects}
        assert resource_types == {"ACTION", "BONUS_ACTION"}

        # Nenhum TRIGGER_CLASS_MECHANIC no action_surge
        mechanic_effects = [
            e for e in surge.effects
            if e.effect_type == SkillEffectType.TRIGGER_CLASS_MECHANIC
        ]
        assert len(mechanic_effects) == 0
