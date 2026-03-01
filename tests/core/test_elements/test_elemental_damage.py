"""Testes para elemental_damage - resolve dano com multiplicador elemental."""

import pytest

from src.core.combat.damage import DamageResult, resolve_damage
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_damage import (
    MIN_ELEMENTAL_DAMAGE,
    ElementalDamageResult,
    resolve_elemental_damage,
)
from src.core.elements.elemental_profile import ElementalProfile


def _make_base_result(final_damage: int = 50) -> DamageResult:
    """Helper para criar DamageResult com dano final especifico."""
    return DamageResult(
        raw_damage=60,
        defense_value=10,
        is_critical=False,
        final_damage=final_damage,
    )


class TestResolveElementalDamage:

    def test_neutral_keeps_same_damage(self) -> None:
        base = _make_base_result(final_damage=50)
        profile = ElementalProfile()
        result = resolve_elemental_damage(base, ElementType.FIRE, profile)
        assert result.final_damage == 50

    def test_weakness_increases_damage(self) -> None:
        base = _make_base_result(final_damage=50)
        profile = ElementalProfile(resistances={ElementType.FIRE: 1.5})
        result = resolve_elemental_damage(base, ElementType.FIRE, profile)
        assert result.final_damage == 75

    def test_resistance_decreases_damage(self) -> None:
        base = _make_base_result(final_damage=50)
        profile = ElementalProfile(resistances={ElementType.ICE: 0.5})
        result = resolve_elemental_damage(base, ElementType.ICE, profile)
        assert result.final_damage == 25

    def test_immune_gives_minimum_damage(self) -> None:
        base = _make_base_result(final_damage=50)
        profile = ElementalProfile(resistances={ElementType.DARKNESS: 0.0})
        result = resolve_elemental_damage(
            base, ElementType.DARKNESS, profile,
        )
        assert result.final_damage == MIN_ELEMENTAL_DAMAGE

    def test_minimum_damage_is_one(self) -> None:
        assert MIN_ELEMENTAL_DAMAGE == 1

    def test_double_weakness(self) -> None:
        base = _make_base_result(final_damage=40)
        profile = ElementalProfile(resistances={ElementType.HOLY: 2.0})
        result = resolve_elemental_damage(base, ElementType.HOLY, profile)
        assert result.final_damage == 80


class TestElementalDamageResultFields:

    def test_element_stored(self) -> None:
        base = _make_base_result()
        profile = ElementalProfile()
        result = resolve_elemental_damage(base, ElementType.FIRE, profile)
        assert result.element is ElementType.FIRE

    def test_multiplier_stored(self) -> None:
        base = _make_base_result()
        profile = ElementalProfile(resistances={ElementType.ICE: 0.5})
        result = resolve_elemental_damage(base, ElementType.ICE, profile)
        assert result.multiplier == 0.5

    def test_base_result_preserved(self) -> None:
        base = _make_base_result(final_damage=50)
        profile = ElementalProfile(resistances={ElementType.FIRE: 1.5})
        result = resolve_elemental_damage(base, ElementType.FIRE, profile)
        assert result.base_result.final_damage == 50

    def test_result_is_frozen(self) -> None:
        base = _make_base_result()
        profile = ElementalProfile()
        result = resolve_elemental_damage(base, ElementType.FIRE, profile)
        with pytest.raises(AttributeError):
            result.final_damage = 999  # type: ignore[misc]


class TestElementalDamageEdgeCases:

    def test_critical_base_with_weakness(self) -> None:
        base = resolve_damage(50, 20, is_critical=True)
        profile = ElementalProfile(resistances={ElementType.FIRE: 1.5})
        result = resolve_elemental_damage(base, ElementType.FIRE, profile)
        assert result.final_damage == int(base.final_damage * 1.5)

    def test_rounds_down(self) -> None:
        base = _make_base_result(final_damage=33)
        profile = ElementalProfile(resistances={ElementType.WATER: 1.5})
        result = resolve_elemental_damage(base, ElementType.WATER, profile)
        assert result.final_damage == 49

    def test_small_damage_with_resistance(self) -> None:
        base = _make_base_result(final_damage=1)
        profile = ElementalProfile(resistances={ElementType.EARTH: 0.5})
        result = resolve_elemental_damage(base, ElementType.EARTH, profile)
        assert result.final_damage == MIN_ELEMENTAL_DAMAGE

    def test_base_result_final_damage_unchanged(self) -> None:
        base = _make_base_result(final_damage=100)
        profile = ElementalProfile(resistances={ElementType.FORCE: 2.0})
        result = resolve_elemental_damage(base, ElementType.FORCE, profile)
        assert result.base_result.final_damage == 100
        assert result.final_damage == 200

    def test_neutral_multiplier_value(self) -> None:
        base = _make_base_result()
        profile = ElementalProfile()
        result = resolve_elemental_damage(base, ElementType.FIRE, profile)
        assert result.multiplier == 1.0
