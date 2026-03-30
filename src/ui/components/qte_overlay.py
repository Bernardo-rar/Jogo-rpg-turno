"""QTE Overlay — visual overlay for Quick Time Event input capture."""

from __future__ import annotations

import pygame

from src.core.combat.qte.qte_config import QteOutcome, QteSequence
from src.core.combat.qte.qte_evaluator import evaluate_qte

_ARROW_MAP = {
    pygame.K_LEFT: "LEFT",
    pygame.K_RIGHT: "RIGHT",
    pygame.K_UP: "UP",
    pygame.K_DOWN: "DOWN",
    pygame.K_a: "LEFT",
    pygame.K_d: "RIGHT",
    pygame.K_w: "UP",
    pygame.K_s: "DOWN",
}

_ARROW_DISPLAY = {
    "LEFT": "\u2190",
    "RIGHT": "\u2192",
    "UP": "\u2191",
    "DOWN": "\u2193",
}

COLOR_PENDING = (200, 200, 200)
COLOR_CORRECT = (80, 255, 80)
COLOR_WRONG = (255, 80, 80)
COLOR_ACTIVE = (255, 255, 100)
COLOR_BG = (20, 20, 40, 200)
COLOR_TIMER = (255, 200, 50)

ARROW_SIZE = 48
ARROW_SPACING = 16
TIMER_BAR_H = 8
OVERLAY_PADDING = 20


class QteOverlay:
    """Captures QTE input and evaluates result."""

    def __init__(self, sequence: QteSequence) -> None:
        self._sequence = sequence
        self._inputs: list[str] = []
        self._states: list[str] = ["pending"] * len(sequence.keys)
        self._elapsed_ms: int = 0
        self._done: bool = False
        self._current_index: int = 0

    @property
    def is_done(self) -> bool:
        return self._done

    def handle_key(self, key: int) -> None:
        """Process a key press during QTE."""
        if self._done:
            return
        arrow = _ARROW_MAP.get(key)
        if arrow is None:
            return
        self._inputs.append(arrow)
        expected = self._sequence.keys[self._current_index]
        if arrow == expected:
            self._states[self._current_index] = "correct"
        else:
            self._states[self._current_index] = "wrong"
        self._current_index += 1
        if self._current_index >= len(self._sequence.keys):
            self._done = True

    def update(self, dt_ms: int) -> None:
        """Update timer. Completes on timeout."""
        if self._done:
            return
        self._elapsed_ms += dt_ms
        if self._elapsed_ms >= self._sequence.time_window_ms:
            self._done = True

    def get_result(self):
        """Returns QteResult after completion."""
        return evaluate_qte(self._sequence, self._inputs)

    def draw(
        self, surface: pygame.Surface, font: pygame.font.Font,
    ) -> None:
        """Draws the QTE overlay centered on screen."""
        sw, sh = surface.get_size()
        n = len(self._sequence.keys)
        total_w = n * ARROW_SIZE + (n - 1) * ARROW_SPACING
        ox = (sw - total_w) // 2
        oy = sh // 2 - ARROW_SIZE // 2
        _draw_qte_background(surface, ox, oy, total_w)
        _draw_qte_title(surface, font, sw, oy)
        self._draw_arrows(surface, font, ox, oy)
        _draw_timer_bar(surface, ox, oy, total_w, self._timer_ratio())

    def _draw_arrows(
        self, surface: pygame.Surface, font: pygame.font.Font,
        ox: int, oy: int,
    ) -> None:
        for i, key_name in enumerate(self._sequence.keys):
            x = ox + i * (ARROW_SIZE + ARROW_SPACING)
            color = self._color_for(self._states[i], i)
            symbol = _ARROW_DISPLAY.get(key_name, "?")
            text = font.render(symbol, True, color)
            tx = x + (ARROW_SIZE - text.get_width()) // 2
            ty = oy + (ARROW_SIZE - text.get_height()) // 2
            surface.blit(text, (tx, ty))

    def _timer_ratio(self) -> float:
        window = max(1, self._sequence.time_window_ms)
        return max(0.0, 1.0 - self._elapsed_ms / window)

    def _color_for(self, state: str, index: int) -> tuple[int, ...]:
        if state == "correct":
            return COLOR_CORRECT
        if state == "wrong":
            return COLOR_WRONG
        if index == self._current_index and not self._done:
            return COLOR_ACTIVE
        return COLOR_PENDING


def _draw_qte_background(
    surface: pygame.Surface, ox: int, oy: int, total_w: int,
) -> None:
    bg_rect = pygame.Rect(
        ox - OVERLAY_PADDING, oy - OVERLAY_PADDING - 20,
        total_w + OVERLAY_PADDING * 2,
        ARROW_SIZE + OVERLAY_PADDING * 2 + 30,
    )
    bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg.fill(COLOR_BG)
    surface.blit(bg, bg_rect.topleft)


def _draw_qte_title(
    surface: pygame.Surface, font: pygame.font.Font, sw: int, oy: int,
) -> None:
    title = font.render("QTE!", True, COLOR_TIMER)
    surface.blit(title, (
        sw // 2 - title.get_width() // 2,
        oy - OVERLAY_PADDING - 16,
    ))


def _draw_timer_bar(
    surface: pygame.Surface,
    ox: int, oy: int, total_w: int, ratio: float,
) -> None:
    timer_y = oy + ARROW_SIZE + 8
    fill_w = int(total_w * ratio)
    pygame.draw.rect(
        surface, (60, 60, 60),
        (ox, timer_y, total_w, TIMER_BAR_H),
    )
    pygame.draw.rect(
        surface, COLOR_TIMER,
        (ox, timer_y, fill_w, TIMER_BAR_H),
    )
