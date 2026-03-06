from __future__ import annotations

import pytest

from src.core.classes.artificer.tech_suit import (
    TechSuit,
    TechSuitConfig,
    load_suit_config,
)

_CONFIG = load_suit_config()


@pytest.fixture
def suit() -> TechSuit:
    return TechSuit(_CONFIG)


# --- Config ---


class TestTechSuitConfig:
    def test_loads_from_json(self) -> None:
        cfg = load_suit_config()
        assert cfg.atk_bonus_at_full == pytest.approx(0.20)

    def test_all_fields_present(self) -> None:
        cfg = load_suit_config()
        assert cfg.phys_def_bonus_at_full == pytest.approx(0.15)
        assert cfg.mag_def_bonus_at_full == pytest.approx(0.20)

    def test_config_is_frozen(self) -> None:
        cfg = load_suit_config()
        with pytest.raises(AttributeError):
            cfg.atk_bonus_at_full = 0.5  # type: ignore[misc]


# --- Mana Ratio ---


class TestManaRatio:
    def test_full_mana(self) -> None:
        assert TechSuit.mana_ratio(100, 100) == pytest.approx(1.0)

    def test_half_mana(self) -> None:
        assert TechSuit.mana_ratio(50, 100) == pytest.approx(0.5)

    def test_empty_mana(self) -> None:
        assert TechSuit.mana_ratio(0, 100) == pytest.approx(0.0)

    def test_zero_max_returns_zero(self) -> None:
        assert TechSuit.mana_ratio(50, 0) == pytest.approx(0.0)

    def test_caps_at_one(self) -> None:
        assert TechSuit.mana_ratio(150, 100) == pytest.approx(1.0)


# --- Multipliers ---


class TestTechSuitMultipliers:
    def test_atk_at_full_mana(self, suit: TechSuit) -> None:
        expected = 1.0 + _CONFIG.atk_bonus_at_full
        assert suit.atk_multiplier(1.0) == pytest.approx(expected)

    def test_atk_at_empty_mana(self, suit: TechSuit) -> None:
        assert suit.atk_multiplier(0.0) == pytest.approx(1.0)

    def test_atk_at_half_mana(self, suit: TechSuit) -> None:
        expected = 1.0 + 0.5 * _CONFIG.atk_bonus_at_full
        assert suit.atk_multiplier(0.5) == pytest.approx(expected)

    def test_phys_def_at_full_mana(self, suit: TechSuit) -> None:
        expected = 1.0 + _CONFIG.phys_def_bonus_at_full
        assert suit.phys_def_multiplier(1.0) == pytest.approx(expected)

    def test_phys_def_at_empty_mana(self, suit: TechSuit) -> None:
        assert suit.phys_def_multiplier(0.0) == pytest.approx(1.0)

    def test_mag_def_at_full_mana(self, suit: TechSuit) -> None:
        expected = 1.0 + _CONFIG.mag_def_bonus_at_full
        assert suit.mag_def_multiplier(1.0) == pytest.approx(expected)

    def test_mag_def_at_empty_mana(self, suit: TechSuit) -> None:
        assert suit.mag_def_multiplier(0.0) == pytest.approx(1.0)
