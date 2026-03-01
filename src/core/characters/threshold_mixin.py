"""Mixin para calculo de threshold bonuses."""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator


class ThresholdBonusMixin:
    """Calcula e cacheia threshold bonuses de atributos."""

    _attributes: Attributes
    _threshold_calc: ThresholdCalculator
    _threshold_cache: dict[str, int] | None

    def get_threshold_bonuses(self) -> dict[str, int]:
        """Agrega bonus de threshold de todos os 7 atributos (cached)."""
        if self._threshold_cache is not None:
            return self._threshold_cache
        total: dict[str, int] = {}
        for attr_type in AttributeType:
            value = self._attributes.get(attr_type)
            bonuses = self._threshold_calc.calculate_bonuses(attr_type, value)
            for key, bonus in bonuses.items():
                total[key] = total.get(key, 0) + bonus
        self._threshold_cache = total
        return total

    def invalidate_threshold_cache(self) -> None:
        """Invalida cache de threshold bonuses (chamar apos mudar atributos)."""
        self._threshold_cache = None
