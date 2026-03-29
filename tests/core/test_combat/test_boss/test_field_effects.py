"""Tests for BossFieldEffect — persistent battlefield conditions."""

from src.core.combat.boss.boss_field_effect import (
    BossFieldConfig,
    BossFieldEffect,
)
from src.core.effects.effect_category import EffectCategory


def _make_config(**overrides) -> BossFieldConfig:
    defaults = {
        "field_id": "lava_floor",
        "name": "Lava Floor",
        "element": "FIRE",
        "damage_pct_max_hp": 0.08,
        "debuff_stat": None,
        "debuff_percent": 0.0,
        "duration": 3,
        "cleanse_element": "WATER",
        "trigger_message": "The ground erupts in molten lava!",
    }
    defaults.update(overrides)
    return BossFieldConfig(**defaults)


class TestBossFieldConfig:

    def test_from_dict(self) -> None:
        data = {
            "field_id": "blizzard",
            "name": "Blizzard",
            "element": "ICE",
            "damage_pct_max_hp": 0.05,
            "debuff_stat": "SPEED",
            "debuff_percent": 20.0,
            "duration": 4,
            "cleanse_element": "FIRE",
            "trigger_message": "A blizzard rages!",
        }
        cfg = BossFieldConfig.from_dict(data)
        assert cfg.field_id == "blizzard"
        assert cfg.debuff_stat == "SPEED"

    def test_from_dict_defaults(self) -> None:
        data = {
            "field_id": "x",
            "name": "X",
            "element": "FIRE",
            "damage_pct_max_hp": 0.1,
            "duration": 2,
            "trigger_message": "!",
        }
        cfg = BossFieldConfig.from_dict(data)
        assert cfg.debuff_stat is None
        assert cfg.cleanse_element is None


class TestBossFieldEffect:

    def test_name(self) -> None:
        effect = BossFieldEffect(_make_config())
        assert effect.name == "Lava Floor"

    def test_stacking_key(self) -> None:
        effect = BossFieldEffect(_make_config())
        assert effect.stacking_key == "boss_field"

    def test_category_is_debuff(self) -> None:
        effect = BossFieldEffect(_make_config())
        assert effect.category == EffectCategory.DEBUFF

    def test_duration(self) -> None:
        effect = BossFieldEffect(_make_config(duration=3))
        assert effect.duration == 3

    def test_tick_returns_damage_based_on_pct(self) -> None:
        effect = BossFieldEffect(_make_config(damage_pct_max_hp=0.08))
        dmg = effect.compute_damage(100)
        assert dmg == 8

    def test_tick_rounds_down(self) -> None:
        effect = BossFieldEffect(_make_config(damage_pct_max_hp=0.08))
        dmg = effect.compute_damage(55)
        assert dmg == 4

    def test_tick_minimum_1(self) -> None:
        effect = BossFieldEffect(_make_config(damage_pct_max_hp=0.01))
        dmg = effect.compute_damage(5)
        assert dmg >= 1

    def test_expires_after_duration(self) -> None:
        effect = BossFieldEffect(_make_config(duration=2))
        effect.tick()
        effect.tick()
        assert effect.is_expired

    def test_not_expired_before_duration(self) -> None:
        effect = BossFieldEffect(_make_config(duration=3))
        effect.tick()
        assert not effect.is_expired

    def test_config_accessible(self) -> None:
        cfg = _make_config()
        effect = BossFieldEffect(cfg)
        assert effect.config is cfg

    def test_can_cleanse_with_matching_element(self) -> None:
        effect = BossFieldEffect(_make_config(cleanse_element="WATER"))
        assert effect.can_cleanse("WATER")

    def test_cannot_cleanse_with_wrong_element(self) -> None:
        effect = BossFieldEffect(_make_config(cleanse_element="WATER"))
        assert not effect.can_cleanse("FIRE")

    def test_no_cleanse_element_means_uncleansable(self) -> None:
        effect = BossFieldEffect(_make_config(cleanse_element=None))
        assert not effect.can_cleanse("WATER")
