"""StatusAilment ABC - base para todos os 13 status ailments."""

from __future__ import annotations

from src.core.effects.effect import Effect
from src.core.effects.effect_category import EffectCategory


class StatusAilment(Effect):
    """Base de todos os status ailments.

    Fornece category=AILMENT e stacking_key padrao 'ailment_{ailment_id}'.
    name e ailment_id sao auto-derivados do class name por default.
    """

    @property
    def name(self) -> str:
        """Nome do ailment. Default: class name."""
        return type(self).__name__

    @property
    def ailment_id(self) -> str:
        """Identificador unico do ailment. Default: class name em lowercase."""
        return type(self).__name__.lower()

    @property
    def stacking_key(self) -> str:
        """'ailment_{ailment_id}'."""
        return f"ailment_{self.ailment_id}"

    @property
    def category(self) -> EffectCategory:
        """Sempre AILMENT."""
        return EffectCategory.AILMENT

    @property
    def is_crowd_control(self) -> bool:
        """True se e um CC ailment. Override em CcAilment."""
        return False

    @property
    def redirects_target(self) -> bool:
        """True se redireciona alvo de ataques. Override em Confusion."""
        return False
