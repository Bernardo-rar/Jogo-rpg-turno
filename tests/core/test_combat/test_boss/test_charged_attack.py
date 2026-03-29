"""Tests for ChargeStateEffect and charged attack config."""

from src.core.combat.boss.charged_attack import (
    ChargedAttackConfig,
    ChargeStateEffect,
)
from src.core.effects.effect_category import EffectCategory


def _make_config() -> ChargedAttackConfig:
    return ChargedAttackConfig(
        attack_id="golem_earthquake",
        name="Earthquake",
        charge_message="The Ancient Golem raises its fists!",
        release_message="The earth shatters!",
        damage_mult=2.5,
        target_type="ALL_ENEMIES",
        element="EARTH",
        aoe_falloff=0.7,
    )


class TestChargedAttackConfig:

    def test_from_dict(self) -> None:
        data = {
            "attack_id": "slam",
            "name": "Slam",
            "charge_message": "Charging...",
            "release_message": "Slam!",
            "damage_mult": 2.0,
            "target_type": "SINGLE_ENEMY",
            "element": "PHYSICAL",
            "aoe_falloff": 1.0,
        }
        cfg = ChargedAttackConfig.from_dict(data)
        assert cfg.attack_id == "slam"
        assert cfg.damage_mult == 2.0

    def test_from_dict_defaults(self) -> None:
        data = {
            "attack_id": "x",
            "name": "X",
            "charge_message": "...",
            "release_message": "!",
            "damage_mult": 1.5,
        }
        cfg = ChargedAttackConfig.from_dict(data)
        assert cfg.target_type == "ALL_ENEMIES"
        assert cfg.aoe_falloff == 1.0
        assert cfg.element is None


class TestChargeStateEffect:

    def test_name(self) -> None:
        effect = ChargeStateEffect(_make_config())
        assert "Earthquake" in effect.name

    def test_stacking_key(self) -> None:
        effect = ChargeStateEffect(_make_config())
        assert effect.stacking_key == "boss_charge"

    def test_category_is_debuff(self) -> None:
        effect = ChargeStateEffect(_make_config())
        assert effect.category == EffectCategory.DEBUFF

    def test_duration_is_one(self) -> None:
        effect = ChargeStateEffect(_make_config())
        assert effect.duration == 1

    def test_tick_returns_skip_turn(self) -> None:
        effect = ChargeStateEffect(_make_config())
        result = effect.tick()
        assert result.skip_turn is True

    def test_tick_message_is_charge_message(self) -> None:
        effect = ChargeStateEffect(_make_config())
        result = effect.tick()
        assert result.message == "The Ancient Golem raises its fists!"

    def test_expires_after_one_tick(self) -> None:
        effect = ChargeStateEffect(_make_config())
        effect.tick()
        assert effect.is_expired

    def test_config_accessible(self) -> None:
        cfg = _make_config()
        effect = ChargeStateEffect(cfg)
        assert effect.config is cfg

    def test_charge_is_interruptible_by_cc(self) -> None:
        """Se o boss receber CC que faz skip_turn, o charge expira."""
        effect = ChargeStateEffect(_make_config())
        effect.force_expire()
        assert effect.is_expired
