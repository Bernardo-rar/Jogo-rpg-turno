"""Testes para ConsumableEffectType enum."""

from __future__ import annotations

from src.core.items.consumable_effect_type import ConsumableEffectType


class TestConsumableEffectType:
    def test_has_heal_hp(self) -> None:
        assert ConsumableEffectType.HEAL_HP is not None

    def test_has_heal_mana(self) -> None:
        assert ConsumableEffectType.HEAL_MANA is not None

    def test_has_damage(self) -> None:
        assert ConsumableEffectType.DAMAGE is not None

    def test_has_buff(self) -> None:
        assert ConsumableEffectType.BUFF is not None

    def test_has_cleanse(self) -> None:
        assert ConsumableEffectType.CLEANSE is not None

    def test_has_flee(self) -> None:
        assert ConsumableEffectType.FLEE is not None

    def test_has_six_members(self) -> None:
        assert len(ConsumableEffectType) == 6
