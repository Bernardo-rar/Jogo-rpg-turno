"""Protocol para cenas do jogo."""

from __future__ import annotations

from typing import Protocol

import pygame


class Scene(Protocol):
    """Interface para cenas renderizaveis."""

    def handle_event(self, event: pygame.event.Event) -> None: ...

    def update(self, dt_ms: int) -> bool:
        """Atualiza estado. Retorna False para encerrar."""
        ...

    def draw(self, surface: pygame.Surface) -> None: ...
