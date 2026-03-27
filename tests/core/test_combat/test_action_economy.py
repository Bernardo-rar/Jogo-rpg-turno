import pytest

from src.core.combat.action_economy import ActionEconomy, ActionType


class TestActionType:
    def test_has_four_action_types(self):
        assert len(list(ActionType)) == 4

    def test_action_exists(self):
        assert ActionType.ACTION is not None

    def test_bonus_action_exists(self):
        assert ActionType.BONUS_ACTION is not None

    def test_reaction_exists(self):
        assert ActionType.REACTION is not None


class TestActionEconomyInitial:
    def test_all_actions_available_on_creation(self):
        economy = ActionEconomy()
        assert economy.is_available(ActionType.ACTION) is True
        assert economy.is_available(ActionType.BONUS_ACTION) is True
        assert economy.is_available(ActionType.REACTION) is True


class TestActionEconomyUse:
    def test_use_action_succeeds(self):
        economy = ActionEconomy()
        result = economy.use(ActionType.ACTION)
        assert result is True

    def test_used_action_becomes_unavailable(self):
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        assert economy.is_available(ActionType.ACTION) is False

    def test_use_already_used_action_fails(self):
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        result = economy.use(ActionType.ACTION)
        assert result is False

    def test_using_one_action_does_not_affect_others(self):
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        assert economy.is_available(ActionType.BONUS_ACTION) is True
        assert economy.is_available(ActionType.REACTION) is True

    def test_use_bonus_action(self):
        economy = ActionEconomy()
        economy.use(ActionType.BONUS_ACTION)
        assert economy.is_available(ActionType.BONUS_ACTION) is False

    def test_use_reaction(self):
        economy = ActionEconomy()
        economy.use(ActionType.REACTION)
        assert economy.is_available(ActionType.REACTION) is False

    def test_use_all_three_actions(self):
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        economy.use(ActionType.BONUS_ACTION)
        economy.use(ActionType.REACTION)
        assert economy.is_available(ActionType.ACTION) is False
        assert economy.is_available(ActionType.BONUS_ACTION) is False
        assert economy.is_available(ActionType.REACTION) is False


class TestActionEconomyReset:
    def test_reset_restores_all_actions(self):
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        economy.use(ActionType.BONUS_ACTION)
        economy.use(ActionType.REACTION)
        economy.reset()
        assert economy.is_available(ActionType.ACTION) is True
        assert economy.is_available(ActionType.BONUS_ACTION) is True
        assert economy.is_available(ActionType.REACTION) is True

    def test_reset_on_fresh_economy_is_safe(self):
        economy = ActionEconomy()
        economy.reset()
        assert economy.is_available(ActionType.ACTION) is True


class TestActionEconomyHasActions:
    def test_has_actions_when_fresh(self):
        economy = ActionEconomy()
        assert economy.has_actions is True

    def test_has_actions_after_using_one(self):
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        assert economy.has_actions is True

    def test_no_actions_after_using_action_and_bonus(self):
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        economy.use(ActionType.BONUS_ACTION)
        assert economy.has_actions is False

    def test_reaction_does_not_count_for_has_actions(self):
        economy = ActionEconomy()
        economy.use(ActionType.REACTION)
        assert economy.has_actions is True
