"""Testes para StatDebuff - debuff concreto de stats."""

import pytest

from src.core.effects.effect import PERMANENT_DURATION
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stacking import StackingPolicy
from src.core.effects.stat_debuff import StatDebuff
from src.core.effects.stat_modifier import StatModifier


class TestStatDebuffCreation:

    def test_create_with_flat_reduction(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3)
        assert debuff.duration == 3
        assert not debuff.is_expired

    def test_create_with_percent_reduction(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, percent=-15.0)
        debuff = StatDebuff(modifier=modifier, duration=4)
        assert debuff.duration == 4

    def test_create_with_flat_and_percent_reduction(self) -> None:
        modifier = StatModifier(
            stat=ModifiableStat.MAGICAL_DEFENSE, flat=-3, percent=-10.0,
        )
        debuff = StatDebuff(modifier=modifier, duration=2)
        assert debuff.modifier.flat == -3
        assert debuff.modifier.percent == -10.0

    def test_create_with_source(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3, source="poison_cloud")
        assert debuff.source == "poison_cloud"

    def test_create_without_source_defaults_empty(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3)
        assert debuff.source == ""


class TestStatDebuffValidation:

    def test_positive_flat_raises_value_error(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=5)
        with pytest.raises(ValueError, match="non-positive"):
            StatDebuff(modifier=modifier, duration=3)

    def test_positive_percent_raises_value_error(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, percent=10.0)
        with pytest.raises(ValueError, match="non-positive"):
            StatDebuff(modifier=modifier, duration=3)

    def test_zero_flat_and_zero_percent_raises_value_error(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK)
        with pytest.raises(ValueError, match="at least one"):
            StatDebuff(modifier=modifier, duration=3)

    def test_duration_zero_raises_value_error(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        with pytest.raises(ValueError, match="duration"):
            StatDebuff(modifier=modifier, duration=0)

    def test_permanent_duration_is_valid(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=PERMANENT_DURATION)
        assert debuff.duration == PERMANENT_DURATION


class TestStatDebuffProperties:

    def test_name_auto_generated_from_stat(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3)
        assert debuff.name == "Physical Defense Down"

    def test_stacking_key_without_source(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3)
        assert debuff.stacking_key == "debuff_speed"

    def test_stacking_key_with_source(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3, source="curse")
        assert debuff.stacking_key == "debuff_speed_curse"

    def test_category_is_debuff(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3)
        assert debuff.category == EffectCategory.DEBUFF

    def test_modifier_returns_stored_modifier(self) -> None:
        modifier = StatModifier(
            stat=ModifiableStat.MAGICAL_ATTACK, flat=-8, percent=-15.0,
        )
        debuff = StatDebuff(modifier=modifier, duration=3)
        assert debuff.modifier is modifier


class TestStatDebuffBehavior:

    def test_get_modifiers_returns_single_modifier(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3)
        result = debuff.get_modifiers()
        assert len(result) == 1
        assert result[0] is modifier

    def test_duration_decrements_on_tick(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3)
        debuff.tick()
        assert debuff.remaining_turns == 2

    def test_expires_after_duration(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=2)
        debuff.tick()
        debuff.tick()
        assert debuff.is_expired

    def test_permanent_debuff_never_expires(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=PERMANENT_DURATION)
        for _ in range(100):
            debuff.tick()
        assert not debuff.is_expired


class TestStatDebuffWithManager:

    def test_manager_aggregates_debuff_modifier(self) -> None:
        manager = EffectManager()
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=-5)
        debuff = StatDebuff(modifier=modifier, duration=3)
        manager.add_effect(debuff)
        agg = manager.aggregate_modifier(ModifiableStat.PHYSICAL_DEFENSE)
        assert agg.flat == -5

    def test_debuff_replace_policy_replaces_same_key(self) -> None:
        manager = EffectManager()
        mod1 = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        mod2 = StatModifier(stat=ModifiableStat.SPEED, flat=-8)
        debuff1 = StatDebuff(modifier=mod1, duration=3)
        debuff2 = StatDebuff(modifier=mod2, duration=3)
        manager.add_effect(debuff1)
        manager.add_effect(debuff2)
        assert manager.count == 1
        agg = manager.aggregate_modifier(ModifiableStat.SPEED)
        assert agg.flat == -8

    def test_debuff_stack_policy_stacks_same_key(self) -> None:
        manager = EffectManager()
        manager.set_stacking_policy("debuff_speed", StackingPolicy.STACK)
        mod1 = StatModifier(stat=ModifiableStat.SPEED, flat=-5)
        mod2 = StatModifier(stat=ModifiableStat.SPEED, flat=-3)
        debuff1 = StatDebuff(modifier=mod1, duration=3)
        debuff2 = StatDebuff(modifier=mod2, duration=3)
        manager.add_effect(debuff1)
        manager.add_effect(debuff2)
        assert manager.count == 2
        agg = manager.aggregate_modifier(ModifiableStat.SPEED)
        assert agg.flat == -8
