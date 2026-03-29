"""ConfirmDialog — reusable yes/no confirmation overlay."""

from __future__ import annotations

import pygame

from src.ui import colors

_BOX_W = 360
_BOX_H = 140
_BORDER_RADIUS = 8
_BG_COLOR = (30, 30, 50, 230)
_BORDER_COLOR = colors.MENU_BORDER
_YES_COLOR = (80, 255, 80)
_NO_COLOR = (255, 80, 80)


class ConfirmDialog:
    """Modal yes/no dialog. Blocks input until answered."""

    def __init__(self, message: str) -> None:
        self._message = message
        self._selected: int = 1  # 0=Yes, 1=No (default No)
        self._result: bool | None = None

    @property
    def is_done(self) -> bool:
        return self._result is not None

    @property
    def confirmed(self) -> bool:
        return self._result is True

    def handle_key(self, key: int) -> None:
        """Process input. LEFT/RIGHT toggle, ENTER confirms."""
        if key in (pygame.K_LEFT, pygame.K_a):
            self._selected = 0
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._selected = 1
        elif key == pygame.K_RETURN:
            self._result = self._selected == 0
        elif key == pygame.K_ESCAPE:
            self._result = False

    def draw(
        self, surface: pygame.Surface, font: pygame.font.Font,
    ) -> None:
        """Draws centered dialog box with message and Yes/No."""
        sw, sh = surface.get_size()
        bx = (sw - _BOX_W) // 2
        by = (sh - _BOX_H) // 2
        overlay = pygame.Surface((_BOX_W, _BOX_H), pygame.SRCALPHA)
        overlay.fill(_BG_COLOR)
        surface.blit(overlay, (bx, by))
        pygame.draw.rect(
            surface, _BORDER_COLOR,
            (bx, by, _BOX_W, _BOX_H), 2, _BORDER_RADIUS,
        )
        msg = font.render(self._message, True, colors.TEXT_WHITE)
        surface.blit(msg, (
            bx + (_BOX_W - msg.get_width()) // 2,
            by + 25,
        ))
        yes_color = _YES_COLOR if self._selected == 0 else colors.TEXT_MUTED
        no_color = _NO_COLOR if self._selected == 1 else colors.TEXT_MUTED
        yes_text = font.render("[Sim]", True, yes_color)
        no_text = font.render("[Nao]", True, no_color)
        mid = bx + _BOX_W // 2
        surface.blit(yes_text, (mid - 80, by + 85))
        surface.blit(no_text, (mid + 30, by + 85))
