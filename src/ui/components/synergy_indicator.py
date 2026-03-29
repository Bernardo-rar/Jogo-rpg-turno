"""Synergy indicator — visual link between synergy-bound enemies."""

from __future__ import annotations

import pygame

SYNERGY_COLOR = (180, 130, 255)
SYNERGY_LINE_WIDTH = 2
SYNERGY_DOT_RADIUS = 4


def draw_synergy_links(
    surface: pygame.Surface,
    card_rects: list[tuple[int, int, int, int]],
) -> None:
    """Draws lines connecting cards that share a synergy.

    card_rects: list of (x, y, w, h) for each synergy member.
    """
    if len(card_rects) < 2:
        return
    centers = [
        (x + w // 2, y + h // 2) for x, y, w, h in card_rects
    ]
    for i in range(len(centers) - 1):
        pygame.draw.line(
            surface, SYNERGY_COLOR,
            centers[i], centers[i + 1],
            SYNERGY_LINE_WIDTH,
        )
    for cx, cy in centers:
        pygame.draw.circle(surface, SYNERGY_COLOR, (cx, cy), SYNERGY_DOT_RADIUS)
