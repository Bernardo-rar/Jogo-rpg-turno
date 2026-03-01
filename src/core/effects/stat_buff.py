"""StatBuff - buff concreto que aumenta um stat derivado."""

from __future__ import annotations

from src.core.effects.effect import Effect
from src.core.effects.effect_category import EffectCategory
from src.core.effects.stat_effect_helpers import (
    format_stat_name,
    validate_buff_modifier,
    validate_duration,
)
from src.core.effects.stat_modifier import StatModifier


class StatBuff(Effect):
    """Buff que aumenta um stat derivado (flat e/ou percentual).

    Recebe StatModifier no construtor. Valores devem ser nao-negativos.
    Nome e stacking_key sao auto-gerados a partir do stat.
    """

    def __init__(
        self,
        modifier: StatModifier,
        duration: int,
        source: str = "",
    ) -> None:
        validate_duration(duration)
        validate_buff_modifier(modifier)
        super().__init__(duration)
        self._modifier = modifier
        self._source = source

    @property
    def name(self) -> str:
        """Nome auto-gerado: ex 'Physical Attack Up'."""
        return f"{format_stat_name(self._modifier.stat)} Up"

    @property
    def stacking_key(self) -> str:
        """'buff_{stat}' ou 'buff_{stat}_{source}'."""
        base = f"buff_{self._modifier.stat.name.lower()}"
        if self._source:
            return f"{base}_{self._source}"
        return base

    @property
    def category(self) -> EffectCategory:
        """Sempre BUFF."""
        return EffectCategory.BUFF

    @property
    def modifier(self) -> StatModifier:
        """O StatModifier que este buff aplica."""
        return self._modifier

    @property
    def source(self) -> str:
        """Origem do buff (quem/o que aplicou)."""
        return self._source

    def get_modifiers(self) -> list[StatModifier]:
        """Retorna o modifier deste buff."""
        return [self._modifier]
