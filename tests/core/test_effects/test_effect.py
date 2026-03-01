"""Testes para Effect ABC."""

import pytest

from src.core.effects.effect import Effect, PERMANENT_DURATION
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier
from src.core.effects.tick_result import TickResult


# --- Implementacoes concretas de teste ---


class _FlatAttackBuff(Effect):
    """Buff de teste: +10 ataque fisico."""

    @property
    def name(self) -> str:
        return "Attack Buff"

    @property
    def stacking_key(self) -> str:
        return "attack_buff"

    def get_modifiers(self) -> list[StatModifier]:
        return [StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=10)]


class _PoisonDot(Effect):
    """DoT de teste: 5 de dano por tick."""

    DAMAGE_PER_TICK = 5

    @property
    def name(self) -> str:
        return "Poison"

    @property
    def stacking_key(self) -> str:
        return "poison"

    def _do_tick(self) -> TickResult:
        return TickResult(damage=self.DAMAGE_PER_TICK, message="Poison tick")


class _TrackingEffect(Effect):
    """Efeito que rastreia chamadas do lifecycle."""

    def __init__(self, duration: int) -> None:
        super().__init__(duration)
        self.applied = False
        self.tick_count = 0
        self.expired_called = False

    @property
    def name(self) -> str:
        return "Tracker"

    @property
    def stacking_key(self) -> str:
        return "tracker"

    def on_apply(self) -> None:
        self.applied = True

    def _do_tick(self) -> TickResult:
        self.tick_count += 1
        return TickResult()

    def on_expire(self) -> None:
        self.expired_called = True


# --- Testes ---


class TestEffectCreation:
    def test_cannot_instantiate_abstract_effect(self):
        with pytest.raises(TypeError):
            Effect(duration=3)  # type: ignore[abstract]

    def test_concrete_effect_has_name(self):
        buff = _FlatAttackBuff(duration=3)
        assert buff.name == "Attack Buff"

    def test_concrete_effect_has_stacking_key(self):
        buff = _FlatAttackBuff(duration=3)
        assert buff.stacking_key == "attack_buff"

    def test_concrete_effect_has_duration(self):
        buff = _FlatAttackBuff(duration=5)
        assert buff.duration == 5

    def test_remaining_starts_at_duration(self):
        buff = _FlatAttackBuff(duration=4)
        assert buff.remaining_turns == 4


class TestEffectDuration:
    def test_tick_decrements_remaining(self):
        buff = _FlatAttackBuff(duration=3)
        buff.tick()
        assert buff.remaining_turns == 2

    def test_expired_when_remaining_reaches_zero(self):
        buff = _FlatAttackBuff(duration=1)
        buff.tick()
        assert buff.is_expired is True

    def test_not_expired_with_turns_remaining(self):
        buff = _FlatAttackBuff(duration=3)
        buff.tick()
        assert buff.is_expired is False

    def test_permanent_never_expires_from_ticks(self):
        buff = _FlatAttackBuff(duration=PERMANENT_DURATION)
        for _ in range(100):
            buff.tick()
        assert buff.is_expired is False

    def test_permanent_remaining_stays_minus_one(self):
        buff = _FlatAttackBuff(duration=PERMANENT_DURATION)
        buff.tick()
        assert buff.remaining_turns == PERMANENT_DURATION

    def test_force_expire_marks_expired(self):
        buff = _FlatAttackBuff(duration=5)
        buff.force_expire()
        assert buff.is_expired is True

    def test_refresh_duration_resets_remaining(self):
        buff = _FlatAttackBuff(duration=3)
        buff.tick()
        buff.tick()
        assert buff.remaining_turns == 1
        buff.refresh_duration(5)
        assert buff.remaining_turns == 5
        assert buff.is_expired is False


class TestEffectLifecycle:
    def test_on_apply_called(self):
        tracker = _TrackingEffect(duration=3)
        tracker.on_apply()
        assert tracker.applied is True

    def test_tick_calls_do_tick(self):
        tracker = _TrackingEffect(duration=3)
        tracker.tick()
        assert tracker.tick_count == 1

    def test_on_expire_called(self):
        tracker = _TrackingEffect(duration=3)
        tracker.on_expire()
        assert tracker.expired_called is True


class TestEffectModifiers:
    def test_flat_buff_returns_modifiers(self):
        buff = _FlatAttackBuff(duration=3)
        mods = buff.get_modifiers()
        assert len(mods) == 1
        assert mods[0].stat == ModifiableStat.PHYSICAL_ATTACK
        assert mods[0].flat == 10

    def test_default_get_modifiers_returns_empty(self):
        tracker = _TrackingEffect(duration=3)
        assert tracker.get_modifiers() == []

    def test_dot_tick_returns_damage(self):
        poison = _PoisonDot(duration=3)
        result = poison.tick()
        assert result.damage == 5
        assert result.message == "Poison tick"

    def test_buff_tick_returns_empty_result(self):
        buff = _FlatAttackBuff(duration=3)
        result = buff.tick()
        assert result.damage == 0
        assert result.healing == 0

    def test_tick_on_expired_returns_empty_result(self):
        buff = _FlatAttackBuff(duration=1)
        buff.tick()
        assert buff.is_expired is True
        result = buff.tick()
        assert result.damage == 0
