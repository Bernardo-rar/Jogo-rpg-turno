from __future__ import annotations

import pytest

from src.core.classes.bard.musical_groove import (
    MusicalGroove,
    MusicalGrooveConfig,
    load_groove_config,
)

_CONFIG = load_groove_config()


@pytest.fixture
def groove() -> MusicalGroove:
    return MusicalGroove(_CONFIG)


# --- Config ---


class TestMusicalGrooveConfig:
    def test_loads_from_json(self) -> None:
        cfg = load_groove_config()
        assert cfg.max_stacks == 10

    def test_all_fields_present(self) -> None:
        cfg = load_groove_config()
        assert cfg.gain_per_skill == 1
        assert cfg.decay_per_turn == 1
        assert cfg.crescendo_duration == 2

    def test_config_is_frozen(self) -> None:
        cfg = load_groove_config()
        with pytest.raises(AttributeError):
            cfg.max_stacks = 20  # type: ignore[misc]


# --- Stacks ---


class TestMusicalGrooveStacks:
    def test_starts_at_zero(self, groove: MusicalGroove) -> None:
        assert groove.stacks == 0

    def test_gain_increases_stacks(self, groove: MusicalGroove) -> None:
        groove.gain()
        assert groove.stacks == _CONFIG.gain_per_skill

    def test_max_stacks_property(self, groove: MusicalGroove) -> None:
        assert groove.max_stacks == _CONFIG.max_stacks

    def test_gain_caps_at_max(self, groove: MusicalGroove) -> None:
        for _ in range(_CONFIG.max_stacks + 5):
            groove.gain()
        assert groove.stacks == _CONFIG.max_stacks

    def test_decay_decreases_stacks(self, groove: MusicalGroove) -> None:
        groove.gain()
        groove.gain()
        groove.decay()
        assert groove.stacks == 2 - _CONFIG.decay_per_turn

    def test_decay_floors_at_zero(self, groove: MusicalGroove) -> None:
        groove.decay()
        assert groove.stacks == 0


# --- Bonuses ---


class TestMusicalGrooveBonuses:
    def test_buff_bonus_zero_at_zero_stacks(
        self, groove: MusicalGroove
    ) -> None:
        assert groove.buff_bonus == 0.0

    def test_buff_bonus_scales_with_stacks(
        self, groove: MusicalGroove
    ) -> None:
        groove.gain()
        expected = _CONFIG.buff_effectiveness_per_stack
        assert groove.buff_bonus == pytest.approx(expected)

    def test_debuff_bonus_scales_with_stacks(
        self, groove: MusicalGroove
    ) -> None:
        groove.gain()
        groove.gain()
        expected = 2 * _CONFIG.debuff_effectiveness_per_stack
        assert groove.debuff_bonus == pytest.approx(expected)

    def test_speed_bonus_scales_with_stacks(
        self, groove: MusicalGroove
    ) -> None:
        for _ in range(5):
            groove.gain()
        expected = 5 * _CONFIG.speed_bonus_per_stack
        assert groove.speed_bonus == pytest.approx(expected)

    def test_crit_bonus_scales_with_stacks(
        self, groove: MusicalGroove
    ) -> None:
        for _ in range(3):
            groove.gain()
        expected = 3 * _CONFIG.crit_chance_per_stack
        assert groove.crit_bonus == pytest.approx(expected)


# --- Crescendo ---


class TestMusicalGrooveCrescendo:
    def test_not_crescendo_by_default(
        self, groove: MusicalGroove
    ) -> None:
        assert groove.is_crescendo is False

    def test_trigger_crescendo_at_max_stacks(
        self, groove: MusicalGroove
    ) -> None:
        for _ in range(_CONFIG.max_stacks):
            groove.gain()
        result = groove.trigger_crescendo()
        assert result is True
        assert groove.is_crescendo is True

    def test_trigger_crescendo_fails_below_max(
        self, groove: MusicalGroove
    ) -> None:
        groove.gain()
        result = groove.trigger_crescendo()
        assert result is False
        assert groove.is_crescendo is False

    def test_crescendo_amplifies_buff_bonus(
        self, groove: MusicalGroove
    ) -> None:
        for _ in range(_CONFIG.max_stacks):
            groove.gain()
        groove.trigger_crescendo()
        base = _CONFIG.max_stacks * _CONFIG.buff_effectiveness_per_stack
        expected = base + _CONFIG.crescendo_bonus
        assert groove.buff_bonus == pytest.approx(expected)

    def test_crescendo_amplifies_debuff_bonus(
        self, groove: MusicalGroove
    ) -> None:
        for _ in range(_CONFIG.max_stacks):
            groove.gain()
        groove.trigger_crescendo()
        base = _CONFIG.max_stacks * _CONFIG.debuff_effectiveness_per_stack
        expected = base + _CONFIG.crescendo_bonus
        assert groove.debuff_bonus == pytest.approx(expected)

    def test_tick_crescendo_decrements(
        self, groove: MusicalGroove
    ) -> None:
        for _ in range(_CONFIG.max_stacks):
            groove.gain()
        groove.trigger_crescendo()
        groove.tick_crescendo()
        assert groove.is_crescendo is True

    def test_crescendo_expires_and_resets_stacks(
        self, groove: MusicalGroove
    ) -> None:
        for _ in range(_CONFIG.max_stacks):
            groove.gain()
        groove.trigger_crescendo()
        for _ in range(_CONFIG.crescendo_duration):
            groove.tick_crescendo()
        assert groove.is_crescendo is False
        assert groove.stacks == _CONFIG.crescendo_reset_stacks

    def test_tick_crescendo_noop_when_inactive(
        self, groove: MusicalGroove
    ) -> None:
        groove.gain()
        groove.tick_crescendo()
        assert groove.stacks == 1
