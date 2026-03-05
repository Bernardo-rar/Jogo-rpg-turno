import pytest

from src.core.classes.ranger.hunters_mark import (
    HuntersMark,
    HuntersMarkConfig,
    load_hunters_mark_config,
)


class TestHuntersMarkConfig:
    def test_is_frozen(self):
        config = HuntersMarkConfig(armor_penetration_pct=0.20)
        with pytest.raises(AttributeError):
            config.armor_penetration_pct = 0.5

    def test_loads_from_json(self):
        config = load_hunters_mark_config()
        assert isinstance(config, HuntersMarkConfig)

    def test_armor_penetration_pct(self):
        config = load_hunters_mark_config()
        assert config.armor_penetration_pct == 0.20


class TestHuntersMark:
    def test_starts_inactive(self):
        mark = HuntersMark()
        assert not mark.is_active
        assert mark.target_name is None

    def test_mark_target(self):
        mark = HuntersMark()
        mark.mark("Goblin")
        assert mark.is_active
        assert mark.target_name == "Goblin"

    def test_mark_replaces_previous(self):
        mark = HuntersMark()
        mark.mark("Goblin")
        mark.mark("Orc")
        assert mark.target_name == "Orc"

    def test_clear_mark(self):
        mark = HuntersMark()
        mark.mark("Goblin")
        mark.clear()
        assert not mark.is_active
        assert mark.target_name is None

    def test_clear_when_inactive_is_noop(self):
        mark = HuntersMark()
        mark.clear()
        assert not mark.is_active
