"""Main loop Pygame."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.ui import layout

if TYPE_CHECKING:
    from src.ui.scenes.scene import Scene


class Game:
    """Loop principal do Pygame: events -> update -> draw."""

    def __init__(self, scene: Scene) -> None:
        pygame.init()
        self._surface = pygame.display.set_mode(
            (layout.WINDOW_WIDTH, layout.WINDOW_HEIGHT),
        )
        pygame.display.set_caption(layout.WINDOW_TITLE)
        self._clock = pygame.time.Clock()
        self._scene = scene
        self._running = True

    def run(self) -> None:
        """Executa o game loop ate fechar."""
        while self._running:
            dt_ms = self._clock.tick(layout.FPS)
            self._handle_events()
            if not self._running:
                break
            self._running = self._scene.update(dt_ms)
            self._scene.draw(self._surface)
            pygame.display.flip()
        pygame.quit()

    @property
    def current_scene(self) -> Scene:
        """Cena ativa atual."""
        return self._scene

    def set_scene(self, scene: Scene) -> None:
        """Troca a cena ativa."""
        self._scene = scene

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                return
            self._scene.handle_event(event)
