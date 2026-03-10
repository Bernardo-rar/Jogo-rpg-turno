"""Gerenciamento de fontes para Pygame."""

from __future__ import annotations

import pygame


class FontManager:
    """Carrega e disponibiliza fontes em 3 tamanhos."""

    FONT_NAME = "consolas"
    FALLBACK = "monospace"
    SIZE_SMALL = 14
    SIZE_MEDIUM = 18
    SIZE_LARGE = 24

    def __init__(self) -> None:
        name = self.FONT_NAME
        self._small = pygame.font.SysFont(name, self.SIZE_SMALL)
        self._medium = pygame.font.SysFont(name, self.SIZE_MEDIUM)
        self._large = pygame.font.SysFont(name, self.SIZE_LARGE)

    @property
    def small(self) -> pygame.font.Font:
        return self._small

    @property
    def medium(self) -> pygame.font.Font:
        return self._medium

    @property
    def large(self) -> pygame.font.Font:
        return self._large
