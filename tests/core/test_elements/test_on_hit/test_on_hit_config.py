"""Testes para OnHitConfig - configuracao de on-hit por elemento."""

from src.core.elements.element_type import ElementType
from src.core.elements.on_hit.on_hit_config import (
    OnHitConfig,
    load_on_hit_configs,
)


class TestOnHitConfigDefaults:

    def test_default_target_effects_empty(self) -> None:
        config = OnHitConfig()
        assert config.target_effects == ()

    def test_default_self_effects_empty(self) -> None:
        config = OnHitConfig()
        assert config.self_effects == ()

    def test_default_party_healing_zero(self) -> None:
        config = OnHitConfig()
        assert config.party_healing_percent == 0.0

    def test_default_bonus_damage_zero(self) -> None:
        config = OnHitConfig()
        assert config.bonus_damage_percent == 0.0

    def test_default_breaks_shield_false(self) -> None:
        config = OnHitConfig()
        assert config.breaks_shield is False

    def test_default_description_empty(self) -> None:
        config = OnHitConfig()
        assert config.description == ""


class TestLoadOnHitConfigs:

    def test_loads_all_ten_elements(self) -> None:
        configs = load_on_hit_configs()
        assert len(configs) == len(ElementType)

    def test_fire_has_target_effects(self) -> None:
        configs = load_on_hit_configs()
        assert len(configs[ElementType.FIRE].target_effects) > 0

    def test_water_has_self_effects(self) -> None:
        configs = load_on_hit_configs()
        assert len(configs[ElementType.WATER].self_effects) > 0

    def test_holy_has_party_healing(self) -> None:
        configs = load_on_hit_configs()
        assert configs[ElementType.HOLY].party_healing_percent > 0.0

    def test_force_has_bonus_damage(self) -> None:
        configs = load_on_hit_configs()
        assert configs[ElementType.FORCE].bonus_damage_percent > 0.0

    def test_force_breaks_shield(self) -> None:
        configs = load_on_hit_configs()
        assert configs[ElementType.FORCE].breaks_shield is True

    def test_fire_description_not_empty(self) -> None:
        configs = load_on_hit_configs()
        assert configs[ElementType.FIRE].description != ""

    def test_ice_has_two_target_effects(self) -> None:
        configs = load_on_hit_configs()
        assert len(configs[ElementType.ICE].target_effects) == 2
