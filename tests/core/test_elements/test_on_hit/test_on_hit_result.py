"""Testes para OnHitResult - descreve efeitos on-hit de ataques elementais."""

import pytest

from src.core.effects.ailments.burn import Burn
from src.core.elements.on_hit.on_hit_result import OnHitResult


class TestOnHitResultDefaults:

    def test_default_effects_empty(self) -> None:
        result = OnHitResult()
        assert result.effects == ()

    def test_default_self_effects_empty(self) -> None:
        result = OnHitResult()
        assert result.self_effects == ()

    def test_default_bonus_damage_zero(self) -> None:
        result = OnHitResult()
        assert result.bonus_damage == 0

    def test_default_party_healing_zero(self) -> None:
        result = OnHitResult()
        assert result.party_healing == 0

    def test_default_breaks_shield_false(self) -> None:
        result = OnHitResult()
        assert result.breaks_shield is False

    def test_default_description_empty(self) -> None:
        result = OnHitResult()
        assert result.description == ""


class TestOnHitResultWithValues:

    def test_effects_stored(self) -> None:
        burn = Burn(damage_per_tick=5, duration=3)
        result = OnHitResult(effects=(burn,))
        assert len(result.effects) == 1

    def test_self_effects_stored(self) -> None:
        burn = Burn(damage_per_tick=5, duration=3)
        result = OnHitResult(self_effects=(burn,))
        assert len(result.self_effects) == 1

    def test_bonus_damage_stored(self) -> None:
        result = OnHitResult(bonus_damage=25)
        assert result.bonus_damage == 25

    def test_party_healing_stored(self) -> None:
        result = OnHitResult(party_healing=15)
        assert result.party_healing == 15

    def test_breaks_shield_stored(self) -> None:
        result = OnHitResult(breaks_shield=True)
        assert result.breaks_shield is True

    def test_description_stored(self) -> None:
        result = OnHitResult(description="Fire burns!")
        assert result.description == "Fire burns!"

    def test_result_is_frozen(self) -> None:
        result = OnHitResult()
        with pytest.raises(AttributeError):
            result.bonus_damage = 10  # type: ignore[misc]
