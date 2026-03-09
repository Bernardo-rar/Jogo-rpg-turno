"""Testes para consumable_effect_applier."""

from __future__ import annotations

from src.core.combat.combat_engine import EventType
from src.core.combat.consumable_effect_applier import apply_consumable_effect
from src.core.effects.buff_factory import create_flat_buff, create_flat_debuff
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType

from tests.core.test_combat.conftest import _build_char


class TestHealHp:
    def test_restores_hp(self) -> None:
        target = _build_char("Target")
        target.take_damage(5)
        hp_before = target.current_hp
        effect = ConsumableEffect(
            effect_type=ConsumableEffectType.HEAL_HP, base_power=30,
        )
        events = apply_consumable_effect(effect, [target], 1, "User")
        assert target.current_hp > hp_before
        assert events[0].event_type == EventType.HEAL


class TestHealMana:
    def test_restores_mana(self) -> None:
        target = _build_char("Target")
        target.spend_mana(50)
        mana_before = target.current_mana
        effect = ConsumableEffect(
            effect_type=ConsumableEffectType.HEAL_MANA, base_power=30,
        )
        events = apply_consumable_effect(effect, [target], 1, "User")
        assert target.current_mana > mana_before
        assert events[0].event_type == EventType.MANA_RESTORE


class TestDamage:
    def test_reduces_hp(self) -> None:
        target = _build_char("Target")
        hp_before = target.current_hp
        effect = ConsumableEffect(
            effect_type=ConsumableEffectType.DAMAGE, base_power=20,
        )
        events = apply_consumable_effect(effect, [target], 1, "User")
        assert target.current_hp < hp_before
        assert events[0].damage is not None

    def test_element_uses_magical_defense(self) -> None:
        target = _build_char("Target")
        effect = ConsumableEffect(
            effect_type=ConsumableEffectType.DAMAGE, base_power=50,
            element=ElementType.FIRE,
        )
        events = apply_consumable_effect(effect, [target], 1, "User")
        assert events[0].damage is not None
        assert events[0].damage.defense_value == target.magical_defense


class TestBuff:
    def test_adds_to_effect_manager(self) -> None:
        target = _build_char("Target")
        effect = ConsumableEffect(
            effect_type=ConsumableEffectType.BUFF,
            base_power=15, stat=ModifiableStat.PHYSICAL_DEFENSE,
            duration=3,
        )
        events = apply_consumable_effect(effect, [target], 1, "User")
        assert len(target.effect_manager.active_effects) == 1
        assert events[0].event_type == EventType.BUFF


class TestCleanse:
    def test_removes_debuffs(self) -> None:
        target = _build_char("Target")
        debuff = create_flat_debuff(
            ModifiableStat.PHYSICAL_ATTACK, 5, 3,
        )
        target.effect_manager.add_effect(debuff)
        assert len(target.effect_manager.active_effects) == 1
        effect = ConsumableEffect(effect_type=ConsumableEffectType.CLEANSE)
        apply_consumable_effect(effect, [target], 1, "User")
        assert len(target.effect_manager.active_effects) == 0

    def test_keeps_buffs(self) -> None:
        target = _build_char("Target")
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 5, 3)
        target.effect_manager.add_effect(buff)
        effect = ConsumableEffect(effect_type=ConsumableEffectType.CLEANSE)
        apply_consumable_effect(effect, [target], 1, "User")
        assert len(target.effect_manager.active_effects) == 1

    def test_cleanse_event_type(self) -> None:
        target = _build_char("Target")
        effect = ConsumableEffect(effect_type=ConsumableEffectType.CLEANSE)
        events = apply_consumable_effect(effect, [target], 1, "User")
        assert events[0].event_type == EventType.CLEANSE


class TestFlee:
    def test_returns_flee_event(self) -> None:
        effect = ConsumableEffect(effect_type=ConsumableEffectType.FLEE)
        events = apply_consumable_effect(
            effect, [_build_char("User")], 1, "User",
        )
        assert len(events) == 1
        assert events[0].event_type == EventType.FLEE
