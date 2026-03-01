"""Testes para ElementalProfile - fraquezas e resistencias elementais."""

import pytest

from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import (
    IMMUNE_MULTIPLIER,
    NEUTRAL_MULTIPLIER,
    ElementalProfile,
    create_profile,
    load_profiles,
)


class TestGetMultiplier:

    def test_empty_profile_returns_neutral(self) -> None:
        profile = ElementalProfile()
        assert profile.get_multiplier(ElementType.FIRE) == NEUTRAL_MULTIPLIER

    def test_configured_element_returns_value(self) -> None:
        profile = ElementalProfile(resistances={ElementType.FIRE: 1.5})
        assert profile.get_multiplier(ElementType.FIRE) == 1.5

    def test_unconfigured_element_returns_neutral(self) -> None:
        profile = ElementalProfile(resistances={ElementType.FIRE: 1.5})
        assert profile.get_multiplier(ElementType.ICE) == NEUTRAL_MULTIPLIER

    def test_multiple_resistances(self) -> None:
        profile = ElementalProfile(resistances={
            ElementType.FIRE: 0.5,
            ElementType.ICE: 1.5,
        })
        assert profile.get_multiplier(ElementType.FIRE) == 0.5
        assert profile.get_multiplier(ElementType.ICE) == 1.5


class TestWeaknessQueries:

    def test_is_weak_to_above_one(self) -> None:
        profile = ElementalProfile(resistances={ElementType.FIRE: 1.5})
        assert profile.is_weak_to(ElementType.FIRE) is True

    def test_is_weak_to_neutral_returns_false(self) -> None:
        profile = ElementalProfile()
        assert profile.is_weak_to(ElementType.FIRE) is False

    def test_is_weak_to_resistant_returns_false(self) -> None:
        profile = ElementalProfile(resistances={ElementType.FIRE: 0.5})
        assert profile.is_weak_to(ElementType.FIRE) is False

    def test_is_resistant_to_below_one(self) -> None:
        profile = ElementalProfile(resistances={ElementType.ICE: 0.5})
        assert profile.is_resistant_to(ElementType.ICE) is True

    def test_is_resistant_to_neutral_returns_false(self) -> None:
        profile = ElementalProfile()
        assert profile.is_resistant_to(ElementType.ICE) is False

    def test_is_resistant_to_weak_returns_false(self) -> None:
        profile = ElementalProfile(resistances={ElementType.ICE: 1.5})
        assert profile.is_resistant_to(ElementType.ICE) is False

    def test_is_immune_when_zero(self) -> None:
        profile = ElementalProfile(
            resistances={ElementType.DARKNESS: IMMUNE_MULTIPLIER},
        )
        assert profile.is_immune_to(ElementType.DARKNESS) is True

    def test_is_immune_returns_false_for_resistant(self) -> None:
        profile = ElementalProfile(resistances={ElementType.DARKNESS: 0.5})
        assert profile.is_immune_to(ElementType.DARKNESS) is False

    def test_is_immune_negative_multiplier(self) -> None:
        """Multiplicador negativo tambem conta como imune."""
        profile = ElementalProfile(resistances={ElementType.FIRE: -0.5})
        assert profile.is_immune_to(ElementType.FIRE) is True


class TestProfileFrozen:

    def test_profile_is_frozen(self) -> None:
        profile = ElementalProfile()
        with pytest.raises(AttributeError):
            profile.resistances = {}  # type: ignore[misc]


class TestFactoryFunctions:

    def test_create_profile(self) -> None:
        profile = create_profile({ElementType.HOLY: 2.0})
        assert profile.get_multiplier(ElementType.HOLY) == 2.0

    def test_create_empty_profile(self) -> None:
        profile = create_profile({})
        assert profile.get_multiplier(ElementType.FIRE) == NEUTRAL_MULTIPLIER

    def test_load_profiles_from_json(self) -> None:
        profiles = load_profiles()
        assert "neutral" in profiles
        assert "undead" in profiles

    def test_loaded_undead_weak_to_holy(self) -> None:
        profiles = load_profiles()
        assert profiles["undead"].is_weak_to(ElementType.HOLY) is True

    def test_loaded_undead_immune_to_darkness(self) -> None:
        profiles = load_profiles()
        assert profiles["undead"].is_immune_to(ElementType.DARKNESS) is True
