"""ComboDetector - detecta combos elementais via markers no alvo."""

from __future__ import annotations

from src.core.effects.effect_manager import EffectManager
from src.core.elements.combo.combo_config import ComboConfig
from src.core.elements.element_type import ElementType

MARKER_KEY_PREFIX = "element_marker_"


class ComboDetector:
    """Verifica se um ataque elemental dispara combo com markers existentes.

    Recebe o dict de combos registrados via DI.
    """

    def __init__(
        self, combos: dict[frozenset[ElementType], ComboConfig],
    ) -> None:
        self._combos = combos

    def check_combo(
        self,
        element: ElementType,
        target_effects: EffectManager,
    ) -> ComboConfig | None:
        """Retorna ComboConfig se combo disparou, None caso contrario."""
        for key, config in self._combos.items():
            if element not in key:
                continue
            other = self._get_partner_element(key, element)
            if other is None:
                continue
            marker_key = f"{MARKER_KEY_PREFIX}{other.name}"
            if target_effects.has_effect(marker_key):
                return config
        return None

    def _get_partner_element(
        self,
        key: frozenset[ElementType],
        element: ElementType,
    ) -> ElementType | None:
        """Retorna o outro elemento do par, ou None se mesmo elemento."""
        others = key - {element}
        if not others:
            return None
        return next(iter(others))
