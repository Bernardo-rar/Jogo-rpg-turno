"""Testes para event_actions."""

from src.dungeon.events.event_template import EventChoice, EventEffect
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.run.event_actions import apply_event_choice
from src.dungeon.run.run_state import RunState
from tests.core.test_combat.conftest import _build_char


def _make_state() -> RunState:
    fm = MapGenerator().generate(seed=1)
    party = [_build_char("A"), _build_char("B")]
    return RunState(seed=1, party=party, floor_map=fm)


def _make_choice(effects: list[EventEffect]) -> EventChoice:
    return EventChoice(
        label="test",
        effects=tuple(effects),
        result_text="test result",
    )


class TestApplyEventChoiceGold:

    def test_adds_gold(self) -> None:
        state = _make_state()
        choice = _make_choice([EventEffect("GOLD", 30)])
        result = apply_event_choice(state, choice)
        assert state.gold == 30
        assert result["gold_delta"] == 30

    def test_negative_gold_does_not_go_below_zero(self) -> None:
        state = _make_state()
        choice = _make_choice([EventEffect("GOLD", -100)])
        apply_event_choice(state, choice)
        assert state.gold >= 0


class TestApplyEventChoiceHpPercent:

    def test_heals_alive_members(self) -> None:
        state = _make_state()
        for c in state.party:
            c.take_damage(c.max_hp // 2)
        choice = _make_choice([EventEffect("HP_PERCENT", 0.20)])
        result = apply_event_choice(state, choice)
        assert result["hp_delta"] > 0

    def test_damages_alive_members(self) -> None:
        state = _make_state()
        initial_hp = sum(c.current_hp for c in state.party)
        choice = _make_choice([EventEffect("HP_PERCENT", -0.15)])
        apply_event_choice(state, choice)
        final_hp = sum(c.current_hp for c in state.party)
        assert final_hp < initial_hp

    def test_skips_dead_members(self) -> None:
        state = _make_state()
        state.party[0].take_damage(state.party[0].max_hp)
        choice = _make_choice([EventEffect("HP_PERCENT", 0.20)])
        apply_event_choice(state, choice)
        assert not state.party[0].is_alive


class TestApplyEventChoiceManaPercent:

    def test_restores_mana(self) -> None:
        state = _make_state()
        for c in state.party:
            c.spend_mana(c.max_mana // 2)
        choice = _make_choice([EventEffect("MANA_PERCENT", 0.30)])
        result = apply_event_choice(state, choice)
        assert result["mana_delta"] > 0

    def test_drains_mana(self) -> None:
        state = _make_state()
        initial_mana = sum(c.current_mana for c in state.party)
        choice = _make_choice([EventEffect("MANA_PERCENT", -0.15)])
        apply_event_choice(state, choice)
        final_mana = sum(c.current_mana for c in state.party)
        assert final_mana < initial_mana


class TestApplyEventChoiceMultiple:

    def test_applies_multiple_effects(self) -> None:
        state = _make_state()
        effects = [
            EventEffect("GOLD", 50),
            EventEffect("HP_PERCENT", 0.10),
        ]
        choice = _make_choice(effects)
        result = apply_event_choice(state, choice)
        assert state.gold == 50
        assert result["gold_delta"] == 50

    def test_empty_effects_is_safe(self) -> None:
        state = _make_state()
        choice = _make_choice([])
        result = apply_event_choice(state, choice)
        assert result["gold_delta"] == 0
