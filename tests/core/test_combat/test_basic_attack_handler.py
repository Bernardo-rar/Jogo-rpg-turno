"""Testes unitarios para BasicAttackHandler."""

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEvent, TurnContext

from tests.core.test_combat.conftest import _build_char


class TestBasicAttackHandlerNoActions:

    def test_returns_empty_when_no_actions(self) -> None:
        attacker = _build_char("Attacker")
        enemy = _build_char("Enemy")
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        economy.use(ActionType.BONUS_ACTION)
        context = TurnContext(
            combatant=attacker,
            allies=[attacker],
            enemies=[enemy],
            action_economy=economy,
            round_number=1,
        )
        handler = BasicAttackHandler()
        events = handler.execute_turn(context)
        assert events == []


class TestBasicAttackHandlerNoTargets:

    def test_returns_empty_when_no_valid_targets(self) -> None:
        attacker = _build_char("Attacker")
        enemy = _build_char("Enemy")
        enemy.take_damage(enemy.current_hp)
        economy = ActionEconomy()
        context = TurnContext(
            combatant=attacker,
            allies=[attacker],
            enemies=[enemy],
            action_economy=economy,
            round_number=1,
        )
        handler = BasicAttackHandler()
        events = handler.execute_turn(context)
        assert events == []
