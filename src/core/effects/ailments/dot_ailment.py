"""DotAilment ABC - base para Damage over Time ailments."""

from __future__ import annotations

from src.core.effects.ailments.status_ailment import StatusAilment
from src.core.effects.tick_result import TickResult

MINIMUM_DOT_DAMAGE = 1


class DotAilment(StatusAilment):
    """Base para DoTs (Poison, Burn, Virus, Bleed, Scorch).

    Recebe damage_per_tick no construtor. Implementa _do_tick()
    retornando TickResult com dano. Subclasses definem tick_message.
    """

    def __init__(self, damage_per_tick: int, duration: int) -> None:
        if damage_per_tick < MINIMUM_DOT_DAMAGE:
            raise ValueError(
                f"damage_per_tick must be >= {MINIMUM_DOT_DAMAGE}"
                f" (got {damage_per_tick})",
            )
        super().__init__(duration)
        self._damage_per_tick = damage_per_tick

    @property
    def damage_per_tick(self) -> int:
        """Dano aplicado a cada tick."""
        return self._damage_per_tick

    @property
    def tick_message(self) -> str:
        """Mensagem de log do tick. Ex: 'Poison deals 5 damage'."""
        return f"{self.name} deals {self.damage_per_tick} damage"

    def _do_tick(self) -> TickResult:
        """Retorna dano por tick."""
        return TickResult(
            damage=self._damage_per_tick,
            message=self.tick_message,
        )
