"""Gerenciador de animacoes ativas."""

from __future__ import annotations

from typing import Any

class AnimationManager:
    """Gerencia ciclo de vida de animacoes: spawn, update, draw, cleanup."""

    def __init__(self) -> None:
        self._animations: list[Any] = []

    def spawn(self, animation: Any) -> None:
        """Adiciona animacao a lista de ativas."""
        self._animations.append(animation)

    def update(self, dt_ms: int) -> None:
        """Ticka todas as animacoes e remove as finalizadas."""
        for anim in self._animations:
            anim.update(dt_ms)
        self._animations = [a for a in self._animations if not a.is_done]

    def draw(self, surface: Any) -> None:
        """Desenha todas as animacoes ativas."""
        for anim in self._animations:
            anim.draw(surface)

    @property
    def has_active(self) -> bool:
        """True se ha alguma animacao rodando."""
        return len(self._animations) > 0

    @property
    def has_blocking(self) -> bool:
        """True se alguma animacao blocking esta ativa."""
        return any(a.blocking for a in self._animations)

    def get_shake_offset(self, target_name: str) -> tuple[int, int]:
        """Soma offsets de todos os CardShakes ativos para o alvo."""
        dx, dy = 0, 0
        for anim in self._animations:
            if hasattr(anim, 'offset') and hasattr(anim, 'target_name') and anim.target_name == target_name:
                ox, oy = anim.offset
                dx, dy = dx + ox, dy + oy
        return (dx, dy)
