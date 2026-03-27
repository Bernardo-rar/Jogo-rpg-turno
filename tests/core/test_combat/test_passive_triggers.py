"""Tests for new passive reaction triggers and PASSIVE action type."""

from src.core.combat.action_economy import ActionType
from src.core.combat.reaction_system import ReactionTrigger


class TestNewReactionTriggers:
    def test_on_combat_start_exists(self) -> None:
        assert ReactionTrigger.ON_COMBAT_START.value == "on_combat_start"

    def test_on_critical_hit_exists(self) -> None:
        assert ReactionTrigger.ON_CRITICAL_HIT.value == "on_critical_hit"

    def test_on_ally_death_exists(self) -> None:
        assert ReactionTrigger.ON_ALLY_DEATH.value == "on_ally_death"

    def test_on_kill_exists(self) -> None:
        assert ReactionTrigger.ON_KILL.value == "on_kill"

    def test_on_low_hp_exists(self) -> None:
        assert ReactionTrigger.ON_LOW_HP.value == "on_low_hp"

    def test_on_round_start_exists(self) -> None:
        assert ReactionTrigger.ON_ROUND_START.value == "on_round_start"


class TestPassiveActionType:
    def test_passive_action_type_exists(self) -> None:
        assert ActionType.PASSIVE is not None

    def test_passive_is_distinct_from_others(self) -> None:
        assert ActionType.PASSIVE != ActionType.ACTION
        assert ActionType.PASSIVE != ActionType.BONUS_ACTION
        assert ActionType.PASSIVE != ActionType.REACTION

    def test_passive_lookup_by_name(self) -> None:
        assert ActionType["PASSIVE"] == ActionType.PASSIVE
