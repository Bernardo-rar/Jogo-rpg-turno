"""Testes para EffectManager."""

import pytest

from src.core.effects.effect import Effect, PERMANENT_DURATION
from src.core.effects.effect_category import EffectCategory
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stacking import StackingPolicy
from src.core.effects.stat_modifier import StatModifier
from src.core.effects.tick_result import TickResult


# --- Implementacoes concretas de teste ---


class _AttackBuff(Effect):
    """Buff: +10 ataque fisico."""

    @property
    def name(self) -> str:
        return "Attack Buff"

    @property
    def stacking_key(self) -> str:
        return "attack_buff"

    @property
    def category(self) -> EffectCategory:
        return EffectCategory.BUFF

    def get_modifiers(self) -> list[StatModifier]:
        return [StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)]


class _DefenseDebuff(Effect):
    """Debuff: -20% defesa fisica."""

    @property
    def name(self) -> str:
        return "Defense Down"

    @property
    def stacking_key(self) -> str:
        return "defense_debuff"

    @property
    def category(self) -> EffectCategory:
        return EffectCategory.DEBUFF

    def get_modifiers(self) -> list[StatModifier]:
        return [StatModifier(stat=ModifiableStat.PHYSICAL_DEFENSE, percent=-20.0)]


class _SpeedBuff(Effect):
    """Buff: +5 speed flat + 10%."""

    @property
    def name(self) -> str:
        return "Haste"

    @property
    def stacking_key(self) -> str:
        return "speed_buff"

    @property
    def category(self) -> EffectCategory:
        return EffectCategory.BUFF

    def get_modifiers(self) -> list[StatModifier]:
        return [StatModifier(stat=ModifiableStat.SPEED, flat=5, percent=10.0)]


class _PoisonDot(Effect):
    """DoT: 5 dano por tick."""

    @property
    def name(self) -> str:
        return "Poison"

    @property
    def stacking_key(self) -> str:
        return "poison"

    @property
    def category(self) -> EffectCategory:
        return EffectCategory.AILMENT

    def _do_tick(self) -> TickResult:
        return TickResult(damage=5, message="Poison tick")


class _TrackingEffect(Effect):
    """Rastreia chamadas de lifecycle."""

    def __init__(self, duration: int, key: str = "tracker") -> None:
        super().__init__(duration)
        self._key = key
        self.applied = False
        self.expired_called = False
        self.expire_call_count = 0

    @property
    def name(self) -> str:
        return "Tracker"

    @property
    def stacking_key(self) -> str:
        return self._key

    @property
    def category(self) -> EffectCategory:
        return EffectCategory.BUFF

    def on_apply(self) -> None:
        self.applied = True

    def on_expire(self) -> None:
        self.expired_called = True
        self.expire_call_count += 1


# --- Fixtures ---


@pytest.fixture
def manager() -> EffectManager:
    return EffectManager()


# --- Testes ---


class TestEffectManagerInit:
    def test_starts_with_no_effects(self, manager: EffectManager):
        assert manager.active_effects == []

    def test_count_is_zero(self, manager: EffectManager):
        assert manager.count == 0


class TestEffectManagerAdd:
    def test_add_increases_count(self, manager: EffectManager):
        manager.add_effect(_AttackBuff(duration=3))
        assert manager.count == 1

    def test_add_calls_on_apply(self, manager: EffectManager):
        tracker = _TrackingEffect(duration=3)
        manager.add_effect(tracker)
        assert tracker.applied is True

    def test_add_multiple_different(self, manager: EffectManager):
        manager.add_effect(_AttackBuff(duration=3))
        manager.add_effect(_DefenseDebuff(duration=2))
        assert manager.count == 2

    def test_added_appears_in_active(self, manager: EffectManager):
        buff = _AttackBuff(duration=3)
        manager.add_effect(buff)
        assert buff in manager.active_effects


class TestEffectManagerRemove:
    def test_remove_decreases_count(self, manager: EffectManager):
        buff = _AttackBuff(duration=3)
        manager.add_effect(buff)
        manager.remove_effect(buff)
        assert manager.count == 0

    def test_remove_calls_expire_hooks(self, manager: EffectManager):
        tracker = _TrackingEffect(duration=3)
        manager.add_effect(tracker)
        manager.remove_effect(tracker)
        assert tracker.expired_called is True
        assert tracker.is_expired is True

    def test_remove_nonexistent_is_noop(self, manager: EffectManager):
        buff = _AttackBuff(duration=3)
        manager.remove_effect(buff)
        assert manager.count == 0

    def test_remove_by_key_removes_all_matching(self, manager: EffectManager):
        manager.set_stacking_policy("tracker", StackingPolicy.STACK)
        manager.add_effect(_TrackingEffect(duration=3, key="tracker"))
        manager.add_effect(_TrackingEffect(duration=5, key="tracker"))
        manager.add_effect(_AttackBuff(duration=3))
        manager.remove_by_key("tracker")
        assert manager.count == 1

    def test_remove_by_key_returns_count(self, manager: EffectManager):
        manager.set_stacking_policy("tracker", StackingPolicy.STACK)
        manager.add_effect(_TrackingEffect(duration=3, key="tracker"))
        manager.add_effect(_TrackingEffect(duration=5, key="tracker"))
        removed = manager.remove_by_key("tracker")
        assert removed == 2

    def test_remove_by_key_zero_when_none_match(self, manager: EffectManager):
        manager.add_effect(_AttackBuff(duration=3))
        removed = manager.remove_by_key("nonexistent")
        assert removed == 0


class TestEffectManagerTick:
    def test_tick_all_decrements_all(self, manager: EffectManager):
        buff = _AttackBuff(duration=5)
        debuff = _DefenseDebuff(duration=3)
        manager.add_effect(buff)
        manager.add_effect(debuff)
        manager.tick_all()
        assert buff.remaining_turns == 4
        assert debuff.remaining_turns == 2

    def test_tick_all_returns_results(self, manager: EffectManager):
        manager.add_effect(_PoisonDot(duration=3))
        manager.add_effect(_AttackBuff(duration=3))
        results = manager.tick_all()
        assert len(results) == 2
        assert results[0].damage == 5
        assert results[1].damage == 0

    def test_tick_all_auto_expires(self, manager: EffectManager):
        manager.add_effect(_AttackBuff(duration=1))
        manager.tick_all()
        assert manager.count == 0

    def test_tick_all_calls_on_expire_for_expired(self, manager: EffectManager):
        tracker = _TrackingEffect(duration=1)
        manager.add_effect(tracker)
        manager.tick_all()
        assert tracker.expired_called is True

    def test_tick_all_empty_returns_empty(self, manager: EffectManager):
        results = manager.tick_all()
        assert results == []

    def test_on_expire_called_only_once_on_natural_expiry(self, manager: EffectManager):
        tracker = _TrackingEffect(duration=1)
        manager.add_effect(tracker)
        manager.tick_all()
        manager.tick_all()
        assert tracker.expire_call_count == 1

    def test_on_expire_called_only_once_on_remove_after_tick(self, manager: EffectManager):
        tracker = _TrackingEffect(duration=1)
        manager.add_effect(tracker)
        manager.tick_all()
        manager.remove_effect(tracker)
        assert tracker.expire_call_count == 1


class TestEffectManagerStacking:
    def test_default_policy_is_replace(self, manager: EffectManager):
        old_buff = _TrackingEffect(duration=3, key="attack_buff")
        new_buff = _AttackBuff(duration=5)
        manager.add_effect(old_buff)
        manager.add_effect(new_buff)
        assert manager.count == 1
        assert new_buff in manager.active_effects

    def test_replace_removes_old_adds_new(self, manager: EffectManager):
        old = _AttackBuff(duration=3)
        new = _AttackBuff(duration=5)
        manager.add_effect(old)
        manager.add_effect(new)
        assert old.is_expired is True
        assert new in manager.active_effects

    def test_replace_calls_expire_on_old(self, manager: EffectManager):
        old = _TrackingEffect(duration=3, key="attack_buff")
        manager.add_effect(old)
        manager.add_effect(_AttackBuff(duration=5))
        assert old.expired_called is True

    def test_stack_keeps_both(self, manager: EffectManager):
        manager.set_stacking_policy("attack_buff", StackingPolicy.STACK)
        buff1 = _AttackBuff(duration=3)
        buff2 = _AttackBuff(duration=5)
        manager.add_effect(buff1)
        manager.add_effect(buff2)
        assert manager.count == 2

    def test_refresh_resets_duration(self, manager: EffectManager):
        manager.set_stacking_policy("attack_buff", StackingPolicy.REFRESH)
        old = _AttackBuff(duration=3)
        manager.add_effect(old)
        old.tick()
        assert old.remaining_turns == 2
        manager.add_effect(_AttackBuff(duration=5))
        assert manager.count == 1
        assert old.remaining_turns == 5

    def test_set_stacking_policy(self, manager: EffectManager):
        manager.set_stacking_policy("attack_buff", StackingPolicy.STACK)
        manager.add_effect(_AttackBuff(duration=3))
        manager.add_effect(_AttackBuff(duration=3))
        assert manager.count == 2


class TestEffectManagerModifiers:
    def test_get_modifiers_for_stat(self, manager: EffectManager):
        manager.add_effect(_AttackBuff(duration=3))
        manager.add_effect(_DefenseDebuff(duration=3))
        mods = manager.get_modifiers_for(ModifiableStat.PHYSICAL_ATTACK)
        assert len(mods) == 1
        assert mods[0].flat == 10

    def test_aggregate_sums_flat_and_percent(self, manager: EffectManager):
        manager.set_stacking_policy("attack_buff", StackingPolicy.STACK)
        manager.add_effect(_AttackBuff(duration=3))
        manager.add_effect(_AttackBuff(duration=3))
        agg = manager.aggregate_modifier(ModifiableStat.PHYSICAL_ATTACK)
        assert agg.flat == 20
        assert agg.percent == 0.0


class TestEffectManagerQuery:
    def test_has_effect_true_when_present(self, manager: EffectManager):
        manager.add_effect(_AttackBuff(duration=3))
        assert manager.has_effect("attack_buff") is True

    def test_has_effect_false_when_absent(self, manager: EffectManager):
        assert manager.has_effect("attack_buff") is False

    def test_clear_all_removes_and_expires(self, manager: EffectManager):
        tracker1 = _TrackingEffect(duration=3, key="t1")
        tracker2 = _TrackingEffect(duration=5, key="t2")
        manager.add_effect(tracker1)
        manager.add_effect(tracker2)
        manager.clear_all()
        assert manager.count == 0
        assert tracker1.expired_called is True
        assert tracker2.expired_called is True
