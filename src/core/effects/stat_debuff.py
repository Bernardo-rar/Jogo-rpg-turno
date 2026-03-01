"""StatDebuff - debuff concreto que reduz um stat derivado."""

from __future__ import annotations

from src.core.effects.effect import Effect
from src.core.effects.effect_category import EffectCategory
from src.core.effects.stat_effect_helpers import (
    format_stat_name,
    validate_debuff_modifier,
    validate_duration,
)
from src.core.effects.stat_modifier import StatModifier


class StatDebuff(Effect):
    """Debuff que reduz um stat derivado (flat e/ou percentual).

    Recebe StatModifier no construtor. Valores devem ser nao-positivos.
    Nome e stacking_key sao auto-gerados a partir do stat.
    """

    def __init__(
        self,
        modifier: StatModifier,
        duration: int,
        source: str = "",
    ) -> None:
        validate_duration(duration)
        validate_debuff_modifier(modifier)
        super().__init__(duration)
        self._modifier = modifier
        self._source = source

    @property
    def name(self) -> str:
        """Nome auto-gerado: ex 'Physical Defense Down'."""
        return f"{format_stat_name(self._modifier.stat)} Down"

    @property
    def stacking_key(self) -> str:
        """'debuff_{stat}' ou 'debuff_{stat}_{source}'."""
        base = f"debuff_{self._modifier.stat.name.lower()}"
        if self._source:
            return f"{base}_{self._source}"
        return base

    @property
    def category(self) -> EffectCategory:
        """Sempre DEBUFF."""
        return EffectCategory.DEBUFF

    @property
    def modifier(self) -> StatModifier:
        """O StatModifier que este debuff aplica."""
        return self._modifier

    @property
    def source(self) -> str:
        """Origem do debuff (quem/o que aplicou)."""
        return self._source

    def get_modifiers(self) -> list[StatModifier]:
        """Retorna o modifier deste debuff."""
        return [self._modifier]
