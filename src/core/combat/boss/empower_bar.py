"""EmpowerBar — boss empower resource that fills each round."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmpowerBarConfig:
    """Config carregada do boss JSON."""

    max_value: int
    gain_per_round: int
    loss_on_weakness_hit: int
    empowered_atk_mult: float
    empowered_def_mult: float
    empowered_duration: int


class EmpowerBar:
    """Boss empower resource. Fills each round, resets on weakness hit."""

    def __init__(self, config: EmpowerBarConfig) -> None:
        self._config = config
        self._current: int = 0
        self._empowered_remaining: int = 0

    @property
    def current(self) -> int:
        return self._current

    @property
    def is_full(self) -> bool:
        return self._current >= self._config.max_value

    @property
    def is_empowered(self) -> bool:
        return self._empowered_remaining > 0

    @property
    def atk_mult(self) -> float:
        if self.is_empowered:
            return self._config.empowered_atk_mult
        return 1.0

    @property
    def def_mult(self) -> float:
        if self.is_empowered:
            return self._config.empowered_def_mult
        return 1.0

    def tick_round(self) -> bool:
        """Fills bar by gain_per_round. Returns True if bar just became full."""
        if self.is_empowered:
            return False
        self._current = min(
            self._current + self._config.gain_per_round,
            self._config.max_value,
        )
        return self.is_full

    def on_weakness_hit(self) -> None:
        """Reduces bar by loss_on_weakness_hit. No effect while empowered."""
        if self.is_empowered:
            return
        self._current = max(
            0, self._current - self._config.loss_on_weakness_hit,
        )

    def activate_empowered(self) -> None:
        """Enters empowered state, resets bar to 0."""
        self._current = 0
        self._empowered_remaining = self._config.empowered_duration

    def tick_empowered(self) -> bool:
        """Decrements empowered turns. Returns True if it just ended."""
        if self._empowered_remaining <= 0:
            return False
        self._empowered_remaining -= 1
        return self._empowered_remaining == 0
