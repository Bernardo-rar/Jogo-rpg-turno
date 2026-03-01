import pytest

from src.core.classes.cleric.divinity import (
    Divinity,
    DivinityConfig,
    load_divinity_configs,
)


class TestDivinityEnum:
    def test_has_seven_divinities(self):
        assert len(list(Divinity)) == 7

    def test_has_holy(self):
        assert Divinity.HOLY is not None

    def test_has_chaos(self):
        assert Divinity.CHAOS is not None

    def test_has_fire(self):
        assert Divinity.FIRE is not None


class TestDivinityConfig:
    def test_is_frozen(self):
        config = DivinityConfig(healing_bonus=1.0)
        with pytest.raises(AttributeError):
            config.healing_bonus = 2.0

    def test_healing_bonus_stored(self):
        config = DivinityConfig(healing_bonus=1.3)
        assert config.healing_bonus == 1.3


class TestLoadDivinityConfigs:
    def test_loads_from_json(self):
        configs = load_divinity_configs("data/classes/cleric_divinities.json")
        assert isinstance(configs, dict)

    def test_loads_all_seven(self):
        configs = load_divinity_configs("data/classes/cleric_divinities.json")
        assert len(configs) == 7

    def test_holy_has_highest_healing_bonus(self):
        configs = load_divinity_configs("data/classes/cleric_divinities.json")
        assert configs[Divinity.HOLY].healing_bonus == 1.3

    def test_chaos_has_lowest_healing_bonus(self):
        configs = load_divinity_configs("data/classes/cleric_divinities.json")
        assert configs[Divinity.CHAOS].healing_bonus == 0.8

    def test_fire_has_neutral_healing_bonus(self):
        configs = load_divinity_configs("data/classes/cleric_divinities.json")
        assert configs[Divinity.FIRE].healing_bonus == 1.0
