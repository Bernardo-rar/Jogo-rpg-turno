"""Testes para StatBuff - buff concreto de stats."""

import pytest

from src.core.effects.effect import PERMANENT_DURATION
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stacking import StackingPolicy
from src.core.effects.stat_buff import StatBuff
from src.core.effects.stat_modifier import StatModifier


class TestStatBuffCreation:

    def test_create_with_flat_modifier(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=3)
        assert buff.duration == 3
        assert not buff.is_expired

    def test_create_with_percent_modifier(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, percent=20.0)
        buff = StatBuff(modifier=modifier, duration=5)
        assert buff.duration == 5

    def test_create_with_flat_and_percent_modifier(self) -> None:
        modifier = StatModifier(
            stat=ModifiableStat.PHYSICAL_DEFENSE, flat=5, percent=10.0,
        )
        buff = StatBuff(modifier=modifier, duration=2)
        assert buff.modifier.flat == 5
        assert buff.modifier.percent == 10.0

    def test_create_with_source(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=3, source="warrior_rally")
        assert buff.source == "warrior_rally"

    def test_create_without_source_defaults_empty(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=3)
        assert buff.source == ""


class TestStatBuffValidation:

    def test_negative_flat_raises_value_error(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=-5)
        with pytest.raises(ValueError, match="non-negative"):
            StatBuff(modifier=modifier, duration=3)

    def test_negative_percent_raises_value_error(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, percent=-10.0)
        with pytest.raises(ValueError, match="non-negative"):
            StatBuff(modifier=modifier, duration=3)

    def test_zero_flat_and_zero_percent_raises_value_error(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK)
        with pytest.raises(ValueError, match="at least one"):
            StatBuff(modifier=modifier, duration=3)

    def test_duration_zero_raises_value_error(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        with pytest.raises(ValueError, match="duration"):
            StatBuff(modifier=modifier, duration=0)

    def test_permanent_duration_is_valid(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=PERMANENT_DURATION)
        assert buff.duration == PERMANENT_DURATION


class TestStatBuffProperties:

    def test_name_auto_generated_from_stat(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=3)
        assert buff.name == "Physical Attack Up"

    def test_stacking_key_without_source(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=3)
        assert buff.stacking_key == "buff_physical_attack"

    def test_stacking_key_with_source(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=3, source="warrior")
        assert buff.stacking_key == "buff_physical_attack_warrior"

    def test_category_is_buff(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        buff = StatBuff(modifier=modifier, duration=3)
        assert buff.category == EffectCategory.BUFF

    def test_modifier_returns_stored_modifier(self) -> None:
        modifier = StatModifier(
            stat=ModifiableStat.MAGICAL_ATTACK, flat=8, percent=15.0,
        )
        buff = StatBuff(modifier=modifier, duration=3)
        assert buff.modifier is modifier


class TestStatBuffBehavior:

    def test_get_modifiers_returns_single_modifier(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=3)
        result = buff.get_modifiers()
        assert len(result) == 1
        assert result[0] is modifier

    def test_duration_decrements_on_tick(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        buff = StatBuff(modifier=modifier, duration=3)
        buff.tick()
        assert buff.remaining_turns == 2

    def test_expires_after_duration(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        buff = StatBuff(modifier=modifier, duration=2)
        buff.tick()
        buff.tick()
        assert buff.is_expired

    def test_permanent_buff_never_expires(self) -> None:
        modifier = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        buff = StatBuff(modifier=modifier, duration=PERMANENT_DURATION)
        for _ in range(100):
            buff.tick()
        assert not buff.is_expired


class TestStatBuffWithManager:

    def test_manager_aggregates_buff_modifier(self) -> None:
        manager = EffectManager()
        modifier = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)
        buff = StatBuff(modifier=modifier, duration=3)
        manager.add_effect(buff)
        agg = manager.aggregate_modifier(ModifiableStat.PHYSICAL_ATTACK)
        assert agg.flat == 10

    def test_buff_replace_policy_replaces_same_key(self) -> None:
        manager = EffectManager()
        mod1 = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        mod2 = StatModifier(stat=ModifiableStat.SPEED, flat=8)
        buff1 = StatBuff(modifier=mod1, duration=3)
        buff2 = StatBuff(modifier=mod2, duration=3)
        manager.add_effect(buff1)
        manager.add_effect(buff2)
        assert manager.count == 1
        agg = manager.aggregate_modifier(ModifiableStat.SPEED)
        assert agg.flat == 8

    def test_buff_stack_policy_stacks_same_key(self) -> None:
        manager = EffectManager()
        manager.set_stacking_policy("buff_speed", StackingPolicy.STACK)
        mod1 = StatModifier(stat=ModifiableStat.SPEED, flat=5)
        mod2 = StatModifier(stat=ModifiableStat.SPEED, flat=8)
        buff1 = StatBuff(modifier=mod1, duration=3)
        buff2 = StatBuff(modifier=mod2, duration=3)
        manager.add_effect(buff1)
        manager.add_effect(buff2)
        assert manager.count == 2
        agg = manager.aggregate_modifier(ModifiableStat.SPEED)
        assert agg.flat == 13
