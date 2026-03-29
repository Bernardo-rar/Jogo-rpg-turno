"""Testes do slot budget calculator."""

from src.core.skills.slot_budget_calculator import calculate_slot_budget
from src.core.skills.slot_config import SlotConfig, load_slot_config


def _config() -> SlotConfig:
    return load_slot_config()


class TestCalculateSlotBudget:

    def test_level_1_budget_is_base(self) -> None:
        assert calculate_slot_budget(1, _config()) == 8

    def test_level_5_budget(self) -> None:
        # 8 + (5-1)*1 = 12
        assert calculate_slot_budget(5, _config()) == 12

    def test_level_9_budget(self) -> None:
        # 8 + (9-1)*1 = 16
        assert calculate_slot_budget(9, _config()) == 16

    def test_level_10_budget_with_bonus(self) -> None:
        # 8 + (10-1)*1 + 1 = 18
        assert calculate_slot_budget(10, _config()) == 18

    def test_budget_scales_linearly(self) -> None:
        config = _config()
        for level in range(1, 10):
            expected = 8 + (level - 1)
            assert calculate_slot_budget(level, config) == expected


class TestLoadSlotConfig:

    def test_loads_from_json(self) -> None:
        config = load_slot_config()
        assert isinstance(config, SlotConfig)

    def test_base_values(self) -> None:
        config = load_slot_config()
        assert config.base_slot_budget == 8
        assert config.base_slot_count == 3
        assert config.passive_limit == 2
