"""DebuffAilment ABC - base para ailments que reduzem stats."""

from __future__ import annotations

from src.core.effects.ailments.status_ailment import StatusAilment
from src.core.effects.stat_effect_helpers import validate_debuff_modifier
from src.core.effects.stat_modifier import StatModifier


class DebuffAilment(StatusAilment):
    """Base para ailments que reduzem stats (Cold, Weakness, Injury, Sickness).

    Recebe lista de StatModifiers no construtor. Valores devem ser nao-positivos.
    Similar a StatDebuff mas com category=AILMENT.
    """

    def __init__(self, modifiers: list[StatModifier], duration: int) -> None:
        for mod in modifiers:
            validate_debuff_modifier(mod)
        super().__init__(duration)
        self._modifiers = modifiers

    @property
    def modifier(self) -> StatModifier:
        """O primeiro StatModifier (retrocompatibilidade)."""
        return self._modifiers[0]

    def get_modifiers(self) -> list[StatModifier]:
        """Retorna todos os modifiers deste ailment."""
        return list(self._modifiers)
