"""Freeze - CC que impede acao + reduz cura recebida."""

from __future__ import annotations

from src.core.effects.ailments.cc_ailment import CcAilment
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier
from src.core.effects.tick_result import TickResult

HEALING_REDUCTION_PERCENT = 50.0


class Freeze(CcAilment):
    """Congelamento: impede acao por X turnos + reduz cura recebida."""

    def _do_tick(self) -> TickResult:
        """Sempre pula o turno."""
        return TickResult(
            skip_turn=True,
            message="Frozen! Cannot act.",
        )

    def get_modifiers(self) -> list[StatModifier]:
        """Reduz cura recebida enquanto congelado."""
        return [
            StatModifier(
                stat=ModifiableStat.HEALING_RECEIVED,
                percent=-HEALING_REDUCTION_PERCENT,
            ),
        ]
