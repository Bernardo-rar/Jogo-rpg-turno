"""Testes para OnHitGenerator - gera OnHitResult a partir de configs."""

import pytest

from src.core.effects.ailments.burn import Burn
from src.core.effects.ailments.cold import Cold
from src.core.effects.ailments.confusion import Confusion
from src.core.effects.ailments.injury import Injury
from src.core.effects.ailments.paralysis import Paralysis
from src.core.effects.ailments.sickness import Sickness
from src.core.effects.stat_buff import StatBuff
from src.core.effects.stat_debuff import StatDebuff
from src.core.elements.on_hit.on_hit_config import EffectSpec, OnHitConfig
from src.core.elements.on_hit.on_hit_generator import generate_on_hit


class TestFireOnHit:

    def test_creates_burn_on_target(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("burn", {"damage_per_tick": 10, "duration": 3}),
            ),
            description="Fire burns!",
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert len(result.effects) == 1
        assert isinstance(result.effects[0], Burn)

    def test_burn_has_correct_damage(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("burn", {"damage_per_tick": 10, "duration": 3}),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert result.effects[0].damage_per_tick == 10

    def test_description_passed_through(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("burn", {"damage_per_tick": 10, "duration": 3}),
            ),
            description="Fire burns!",
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert result.description == "Fire burns!"


class TestWaterOnHit:

    def test_creates_buff_on_self(self) -> None:
        config = OnHitConfig(
            self_effects=(
                EffectSpec("percent_buff", {
                    "stat": "MAGICAL_ATTACK",
                    "percent": 20.0,
                    "duration": 2,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert len(result.self_effects) == 1
        assert isinstance(result.self_effects[0], StatBuff)

    def test_no_target_effects(self) -> None:
        config = OnHitConfig(
            self_effects=(
                EffectSpec("percent_buff", {
                    "stat": "MAGICAL_ATTACK",
                    "percent": 20.0,
                    "duration": 2,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert len(result.effects) == 0


class TestIceOnHit:

    def test_creates_cold_and_debuff(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("cold", {
                    "duration": 3, "reduction_percent": 20.0,
                }),
                EffectSpec("percent_debuff", {
                    "stat": "PHYSICAL_DEFENSE",
                    "percent": 15.0,
                    "duration": 3,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert len(result.effects) == 2

    def test_first_effect_is_cold(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("cold", {
                    "duration": 3, "reduction_percent": 20.0,
                }),
                EffectSpec("percent_debuff", {
                    "stat": "PHYSICAL_DEFENSE",
                    "percent": 15.0,
                    "duration": 3,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert isinstance(result.effects[0], Cold)

    def test_second_effect_is_debuff(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("cold", {
                    "duration": 3, "reduction_percent": 20.0,
                }),
                EffectSpec("percent_debuff", {
                    "stat": "PHYSICAL_DEFENSE",
                    "percent": 15.0,
                    "duration": 3,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert isinstance(result.effects[1], StatDebuff)


class TestLightningOnHit:

    def test_creates_paralysis_and_sickness(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("paralysis", {"duration": 2}),
                EffectSpec("sickness", {
                    "duration": 3, "reduction_percent": 50.0,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert isinstance(result.effects[0], Paralysis)
        assert isinstance(result.effects[1], Sickness)


class TestEarthOnHit:

    def test_creates_self_buff(self) -> None:
        config = OnHitConfig(
            self_effects=(
                EffectSpec("flat_buff", {
                    "stat": "PHYSICAL_DEFENSE",
                    "flat": 15,
                    "duration": 3,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert len(result.self_effects) == 1
        assert isinstance(result.self_effects[0], StatBuff)


class TestHolyOnHit:

    def test_party_healing_proportional_to_damage(self) -> None:
        config = OnHitConfig(party_healing_percent=0.15)
        result = generate_on_hit(config, damage_dealt=100)
        assert result.party_healing == 15

    def test_party_healing_rounds_down(self) -> None:
        config = OnHitConfig(party_healing_percent=0.15)
        result = generate_on_hit(config, damage_dealt=33)
        assert result.party_healing == 4

    def test_no_target_effects(self) -> None:
        config = OnHitConfig(party_healing_percent=0.15)
        result = generate_on_hit(config, damage_dealt=100)
        assert len(result.effects) == 0


class TestDarknessOnHit:

    def test_creates_burn_for_necrotic(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("burn", {"damage_per_tick": 12, "duration": 3}),
            ),
            description="Necrotic burn!",
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert isinstance(result.effects[0], Burn)
        assert result.effects[0].damage_per_tick == 12


class TestCelestialOnHit:

    def test_party_healing_proportional(self) -> None:
        config = OnHitConfig(party_healing_percent=0.10)
        result = generate_on_hit(config, damage_dealt=200)
        assert result.party_healing == 20

    def test_zero_damage_zero_healing(self) -> None:
        config = OnHitConfig(party_healing_percent=0.10)
        result = generate_on_hit(config, damage_dealt=0)
        assert result.party_healing == 0


class TestPsychicOnHit:

    def test_creates_confusion_and_injury(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("confusion", {"duration": 2}),
                EffectSpec("injury", {
                    "duration": 3, "reduction_percent": 20.0,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert isinstance(result.effects[0], Confusion)
        assert isinstance(result.effects[1], Injury)

    def test_confusion_has_correct_duration(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("confusion", {"duration": 2}),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert result.effects[0].duration == 2


class TestForceOnHit:

    def test_bonus_damage_proportional(self) -> None:
        config = OnHitConfig(bonus_damage_percent=0.25)
        result = generate_on_hit(config, damage_dealt=100)
        assert result.bonus_damage == 25

    def test_breaks_shield_true(self) -> None:
        config = OnHitConfig(breaks_shield=True)
        result = generate_on_hit(config, damage_dealt=100)
        assert result.breaks_shield is True

    def test_no_target_effects(self) -> None:
        config = OnHitConfig(bonus_damage_percent=0.25, breaks_shield=True)
        result = generate_on_hit(config, damage_dealt=100)
        assert len(result.effects) == 0


class TestUnknownEffectType:

    def test_raises_on_unknown_effect_type(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("nonexistent_effect", {"duration": 3}),
            ),
        )
        with pytest.raises(ValueError, match="Unknown effect type"):
            generate_on_hit(config, damage_dealt=50)


class TestFlatDebuffOnHit:

    def test_creates_flat_debuff(self) -> None:
        config = OnHitConfig(
            target_effects=(
                EffectSpec("flat_debuff", {
                    "stat": "PHYSICAL_DEFENSE",
                    "flat": 10,
                    "duration": 3,
                }),
            ),
        )
        result = generate_on_hit(config, damage_dealt=50)
        assert len(result.effects) == 1
        assert isinstance(result.effects[0], StatDebuff)


class TestGeneratorWithJsonConfigs:

    def test_all_elements_generate_without_error(self) -> None:
        from src.core.elements.element_type import ElementType
        from src.core.elements.on_hit.on_hit_config import load_on_hit_configs

        configs = load_on_hit_configs()
        for element in ElementType:
            config = configs[element]
            result = generate_on_hit(config, damage_dealt=50)
            assert result is not None
