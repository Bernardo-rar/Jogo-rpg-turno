import pytest

from src.core.classes.warlock.familiar import (
    FamiliarConfig,
    FamiliarType,
    load_familiar_configs,
)


class TestFamiliarType:
    def test_has_four_types(self):
        assert len(FamiliarType) == 4

    def test_imp_exists(self):
        assert FamiliarType.IMP is not None

    def test_raven_exists(self):
        assert FamiliarType.RAVEN is not None

    def test_spider_exists(self):
        assert FamiliarType.SPIDER is not None

    def test_shadow_cat_exists(self):
        assert FamiliarType.SHADOW_CAT is not None


class TestFamiliarConfig:
    def test_load_from_json(self):
        configs = load_familiar_configs()
        assert len(configs) == 4

    def test_all_types_have_config(self):
        configs = load_familiar_configs()
        for ftype in FamiliarType:
            assert ftype in configs

    def test_config_is_frozen(self):
        configs = load_familiar_configs()
        with pytest.raises(AttributeError):
            configs[FamiliarType.IMP].stat_bonus_pct = 0.99

    def test_imp_boosts_magical_attack(self):
        configs = load_familiar_configs()
        assert configs[FamiliarType.IMP].stat_bonus_type == "magical_attack"

    def test_raven_boosts_speed(self):
        configs = load_familiar_configs()
        assert configs[FamiliarType.RAVEN].stat_bonus_type == "speed"

    def test_shadow_cat_boosts_magical_defense(self):
        configs = load_familiar_configs()
        assert configs[FamiliarType.SHADOW_CAT].stat_bonus_type == "magical_defense"

    def test_all_bonuses_positive(self):
        configs = load_familiar_configs()
        for config in configs.values():
            assert config.stat_bonus_pct > 0.0
