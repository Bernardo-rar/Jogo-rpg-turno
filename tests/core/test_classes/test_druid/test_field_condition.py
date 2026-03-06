from __future__ import annotations

import pytest

from src.core.classes.druid.field_condition import (
    FieldConditionConfig,
    FieldConditionType,
    load_field_condition_configs,
)


class TestFieldConditionTypeEnum:
    def test_has_four_members(self) -> None:
        assert len(FieldConditionType) == 4

    def test_snow_exists(self) -> None:
        assert FieldConditionType.SNOW is not None

    def test_rain_exists(self) -> None:
        assert FieldConditionType.RAIN is not None

    def test_sandstorm_exists(self) -> None:
        assert FieldConditionType.SANDSTORM is not None

    def test_fog_exists(self) -> None:
        assert FieldConditionType.FOG is not None


class TestFieldConditionConfig:
    def test_is_frozen(self) -> None:
        cfg = FieldConditionConfig(
            element_resistance="FIRE",
            element_vulnerability="ICE",
            speed_modifier=0.85,
            default_duration=3,
        )
        with pytest.raises(AttributeError):
            cfg.speed_modifier = 1.0  # type: ignore[misc]

    def test_has_all_fields(self) -> None:
        cfg = FieldConditionConfig(
            element_resistance="FIRE",
            element_vulnerability="ICE",
            speed_modifier=0.85,
            default_duration=3,
        )
        assert cfg.element_resistance == "FIRE"
        assert cfg.element_vulnerability == "ICE"
        assert cfg.speed_modifier == 0.85
        assert cfg.default_duration == 3


class TestLoadFieldConditionConfigs:
    def test_loads_all_four_conditions(self) -> None:
        configs = load_field_condition_configs()
        assert len(configs) == 4

    def test_keys_are_field_condition_enum(self) -> None:
        configs = load_field_condition_configs()
        for key in configs:
            assert isinstance(key, FieldConditionType)

    def test_values_are_config(self) -> None:
        configs = load_field_condition_configs()
        for val in configs.values():
            assert isinstance(val, FieldConditionConfig)

    def test_snow_resists_fire(self) -> None:
        configs = load_field_condition_configs()
        snow = configs[FieldConditionType.SNOW]
        assert snow.element_resistance == "FIRE"

    def test_snow_vulnerable_to_ice(self) -> None:
        configs = load_field_condition_configs()
        snow = configs[FieldConditionType.SNOW]
        assert snow.element_vulnerability == "ICE"

    def test_rain_vulnerable_to_lightning(self) -> None:
        configs = load_field_condition_configs()
        rain = configs[FieldConditionType.RAIN]
        assert rain.element_vulnerability == "LIGHTNING"

    def test_all_have_positive_duration(self) -> None:
        configs = load_field_condition_configs()
        for cfg in configs.values():
            assert cfg.default_duration > 0

    def test_speed_modifiers_are_positive(self) -> None:
        configs = load_field_condition_configs()
        for cfg in configs.values():
            assert cfg.speed_modifier > 0.0
