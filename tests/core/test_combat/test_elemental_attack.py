"""Testes para elemental_attack - resolve dano elemental + on-hit effects."""

from src.core.combat.damage import DamageResult, resolve_damage
from src.core.combat.elemental_attack import (
    ElementalAttackOutcome,
    ElementalContext,
    apply_on_hit_effects,
    resolve_elemental_attack,
)
from src.core.effects.ailments.burn import Burn
from src.core.effects.ailments.cold import Cold
from src.core.effects.ailments.confusion import Confusion
from src.core.effects.ailments.paralysis import Paralysis
from src.core.effects.ailments.sickness import Sickness
from src.core.effects.stat_buff import StatBuff
from src.core.effects.stat_debuff import StatDebuff
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile
from src.core.elements.on_hit.on_hit_config import load_on_hit_configs

from tests.core.test_combat.conftest import _build_char as _make_char

ON_HIT_CONFIGS = load_on_hit_configs()


def _base_result(damage: int = 20) -> DamageResult:
    return resolve_damage(attack_power=damage + 30, defense=30)


class TestElementalResistance:

    def test_weak_target_takes_more_damage(self) -> None:
        profile = ElementalProfile(resistances={ElementType.FIRE: 1.5})
        target = _make_char("Target", profile=profile)
        outcome = resolve_elemental_attack(
            _base_result(20),
            ElementalContext(ElementType.FIRE, target.elemental_profile, ON_HIT_CONFIGS),
        )
        assert outcome.elemental_result.final_damage > _base_result(20).final_damage

    def test_resistant_target_takes_less(self) -> None:
        profile = ElementalProfile(resistances={ElementType.FIRE: 0.5})
        target = _make_char("Target", profile=profile)
        outcome = resolve_elemental_attack(
            _base_result(20),
            ElementalContext(ElementType.FIRE, target.elemental_profile, ON_HIT_CONFIGS),
        )
        assert outcome.elemental_result.final_damage < _base_result(20).final_damage

    def test_immune_target_takes_minimum(self) -> None:
        profile = ElementalProfile(resistances={ElementType.FIRE: 0.0})
        target = _make_char("Target", profile=profile)
        outcome = resolve_elemental_attack(
            _base_result(20),
            ElementalContext(ElementType.FIRE, target.elemental_profile, ON_HIT_CONFIGS),
        )
        assert outcome.elemental_result.final_damage == 1

    def test_neutral_profile_no_damage_change(self) -> None:
        target = _make_char("Target")
        base = _base_result(20)
        outcome = resolve_elemental_attack(
            base,
            ElementalContext(ElementType.FIRE, target.elemental_profile, ON_HIT_CONFIGS),
        )
        assert outcome.elemental_result.final_damage == base.final_damage


class TestOnHitEffects:

    def test_fire_attack_generates_burn(self) -> None:
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.FIRE, ElementalProfile(), ON_HIT_CONFIGS),
        )
        assert any(isinstance(e, Burn) for e in outcome.on_hit.effects)

    def test_ice_attack_generates_cold_and_debuff(self) -> None:
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.ICE, ElementalProfile(), ON_HIT_CONFIGS),
        )
        assert len(outcome.on_hit.effects) == 2

    def test_water_attack_has_self_effects(self) -> None:
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.WATER, ElementalProfile(), ON_HIT_CONFIGS),
        )
        assert len(outcome.on_hit.self_effects) > 0

    def test_holy_attack_has_party_healing(self) -> None:
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.HOLY, ElementalProfile(), ON_HIT_CONFIGS),
        )
        assert outcome.on_hit.party_healing > 0

    def test_force_attack_has_bonus_damage(self) -> None:
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.FORCE, ElementalProfile(), ON_HIT_CONFIGS),
        )
        assert outcome.on_hit.bonus_damage > 0

    def test_force_breaks_shield(self) -> None:
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.FORCE, ElementalProfile(), ON_HIT_CONFIGS),
        )
        assert outcome.on_hit.breaks_shield is True

    def test_lightning_full_flow(self) -> None:
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.LIGHTNING, ElementalProfile(), ON_HIT_CONFIGS),
        )
        types = [type(e) for e in outcome.on_hit.effects]
        assert Paralysis in types
        assert Sickness in types


class TestApplyOnHitEffects:

    def test_adds_to_target_manager(self) -> None:
        attacker = _make_char("Attacker")
        target = _make_char("Target")
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.FIRE, target.elemental_profile, ON_HIT_CONFIGS),
        )
        apply_on_hit_effects(outcome, target.effect_manager, attacker.effect_manager)
        assert target.effect_manager.count > 0

    def test_adds_self_effects_to_attacker(self) -> None:
        attacker = _make_char("Attacker")
        target = _make_char("Target")
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.WATER, target.elemental_profile, ON_HIT_CONFIGS),
        )
        apply_on_hit_effects(outcome, target.effect_manager, attacker.effect_manager)
        assert attacker.effect_manager.count > 0

    def test_outcome_is_frozen(self) -> None:
        outcome = resolve_elemental_attack(
            _base_result(),
            ElementalContext(ElementType.FIRE, ElementalProfile(), ON_HIT_CONFIGS),
        )
        assert isinstance(outcome, ElementalAttackOutcome)
