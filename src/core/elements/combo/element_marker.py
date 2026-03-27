"""ElementMarker - marker temporario que indica qual elemento atingiu o alvo."""

from __future__ import annotations

from src.core.effects.effect import Effect
from src.core.effects.effect_category import EffectCategory
from src.core.effects.tick_result import TickResult
from src.core.elements.element_type import ElementType

MARKER_DURATION = 2


class ElementMarker(Effect):
    """Marker temporario que indica qual elemento atingiu o alvo.

    Dura 1 round completo (duration=2, sobrevive 1 tick).
    Nao causa efeitos colaterais; serve apenas como tag
    para o ComboDetector identificar combinacoes elementais.
    """

    def __init__(self, element: ElementType) -> None:
        super().__init__(duration=MARKER_DURATION)
        self._element = element

    @property
    def name(self) -> str:
        return f"{self._element.name} Mark"

    @property
    def stacking_key(self) -> str:
        return f"element_marker_{self._element.name}"

    @property
    def category(self) -> EffectCategory:
        return EffectCategory.AILMENT

    @property
    def element(self) -> ElementType:
        """Elemento associado a este marker."""
        return self._element

    def _do_tick(self) -> TickResult:
        return TickResult()
