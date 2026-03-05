from __future__ import annotations

from enum import Enum


class EquilibriumState(Enum):
    """Estado atual da barra de Equilibrium."""

    VITALITY = "vitality"
    BALANCED = "balanced"
    DESTRUCTION = "destruction"


class EquilibriumBar:
    """Barra de Equilibrium: desliza entre Vitalidade e Destruicao."""

    def __init__(
        self,
        max_value: int,
        vitality_upper: int,
        destruction_lower: int,
    ) -> None:
        self._max = max_value
        self._vit_upper = vitality_upper
        self._dest_lower = destruction_lower
        self._value = max_value // 2

    @property
    def value(self) -> int:
        return self._value

    @property
    def max_value(self) -> int:
        return self._max

    @property
    def state(self) -> EquilibriumState:
        if self._value <= self._vit_upper:
            return EquilibriumState.VITALITY
        if self._value >= self._dest_lower:
            return EquilibriumState.DESTRUCTION
        return EquilibriumState.BALANCED

    @property
    def vitality_intensity(self) -> float:
        """0.0-1.0: quao fundo na zona Vitality (0 fora)."""
        if self._vit_upper <= 0:
            return 0.0
        if self._value >= self._vit_upper:
            return 0.0
        return (self._vit_upper - self._value) / self._vit_upper

    @property
    def destruction_intensity(self) -> float:
        """0.0-1.0: quao fundo na zona Destruction (0 fora)."""
        dest_range = self._max - self._dest_lower
        if dest_range <= 0:
            return 0.0
        if self._value <= self._dest_lower:
            return 0.0
        return (self._value - self._dest_lower) / dest_range

    def shift_toward_destruction(self, amount: int) -> int:
        """Desloca barra para Destruction. Retorna shift real."""
        actual = min(amount, self._max - self._value)
        self._value += actual
        return actual

    def shift_toward_vitality(self, amount: int) -> int:
        """Desloca barra para Vitality. Retorna shift real."""
        actual = min(amount, self._value)
        self._value -= actual
        return actual

    def decay_toward_center(self, amount: int) -> int:
        """Decai em direcao ao centro. Retorna decaimento real."""
        center = self._max // 2
        distance = abs(self._value - center)
        actual = min(amount, distance)
        if self._value > center:
            self._value -= actual
        else:
            self._value += actual
        return actual
