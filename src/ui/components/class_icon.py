"""Class icons — 16x16 geometric symbols for each class."""

from __future__ import annotations

import pygame

_SIZE = 16
_HALF = _SIZE // 2


def draw_class_icon(
    surface: pygame.Surface,
    class_name: str,
    x: int, y: int,
    color: tuple = (200, 200, 200),
) -> None:
    """Draws a 16x16 class icon at (x, y)."""
    draw_fn = _ICON_DISPATCH.get(class_name.lower())
    if draw_fn is not None:
        draw_fn(surface, x, y, color)


def _draw_fighter(s, x, y, c):
    cx = x + _HALF
    pygame.draw.line(s, c, (cx, y + 2), (cx, y + 14), 2)
    pygame.draw.line(s, c, (cx - 4, y + 5), (cx + 4, y + 5), 2)


def _draw_mage(s, x, y, c):
    cx, cy = x + _HALF, y + _HALF
    pts = [(cx, cy - 6), (cx + 3, cy), (cx, cy + 6), (cx - 3, cy)]
    pygame.draw.polygon(s, c, pts, 2)


def _draw_cleric(s, x, y, c):
    cx, cy = x + _HALF, y + _HALF
    pygame.draw.line(s, c, (cx, cy - 5), (cx, cy + 5), 3)
    pygame.draw.line(s, c, (cx - 5, cy), (cx + 5, cy), 3)


def _draw_barbarian(s, x, y, c):
    pygame.draw.polygon(s, c, [
        (x + _HALF, y + 2), (x + _HALF + 5, y + 10), (x + _HALF - 5, y + 10),
    ])
    pygame.draw.line(s, c, (x + _HALF, y + 10), (x + _HALF, y + 14), 2)


def _draw_paladin(s, x, y, c):
    r = pygame.Rect(x + 3, y + 2, 10, 12)
    pygame.draw.rect(s, c, r, 2, 2)
    cx, cy = r.centerx, r.centery
    pygame.draw.line(s, c, (cx, cy - 3), (cx, cy + 3), 1)
    pygame.draw.line(s, c, (cx - 3, cy), (cx + 3, cy), 1)


def _draw_ranger(s, x, y, c):
    cx = x + _HALF
    pygame.draw.polygon(s, c, [(cx, y + 2), (cx + 3, y + 8), (cx - 3, y + 8)])
    pygame.draw.line(s, c, (cx, y + 8), (cx, y + 14), 2)


def _draw_monk(s, x, y, c):
    cx, cy = x + _HALF, y + _HALF
    pygame.draw.circle(s, c, (cx, cy), 5, 2)
    pygame.draw.line(s, c, (cx - 2, cy), (cx + 2, cy), 2)


def _draw_sorcerer(s, x, y, c):
    cx = x + _HALF
    pts = [(cx, y + 2), (cx + 4, y + 8), (cx, y + 14), (cx - 4, y + 8)]
    pygame.draw.polygon(s, c, pts)


def _draw_warlock(s, x, y, c):
    cx, cy = x + _HALF, y + _HALF
    pygame.draw.ellipse(s, c, (cx - 6, cy - 3, 12, 6), 2)
    pygame.draw.circle(s, c, (cx, cy), 2)


def _draw_druid(s, x, y, c):
    pts = [(x + _HALF, y + 2), (x + _HALF + 5, y + 8),
           (x + _HALF, y + 14), (x + _HALF - 5, y + 8)]
    pygame.draw.polygon(s, c, pts, 2)


def _draw_rogue(s, x, y, c):
    cx = x + _HALF
    pygame.draw.polygon(s, c, [(cx, y + 2), (cx + 2, y + 9), (cx - 2, y + 9)])
    pygame.draw.line(s, c, (cx - 3, y + 7), (cx + 3, y + 7), 1)


def _draw_bard(s, x, y, c):
    cx = x + _HALF
    pygame.draw.circle(s, c, (cx - 1, y + 11), 3)
    pygame.draw.line(s, c, (cx + 2, y + 11), (cx + 2, y + 3), 2)
    pygame.draw.line(s, c, (cx + 2, y + 3), (cx + 5, y + 5), 2)


def _draw_artificer(s, x, y, c):
    cx, cy = x + _HALF, y + _HALF
    pygame.draw.circle(s, c, (cx, cy), 5, 2)
    for angle_deg in (0, 90, 180, 270):
        import math
        rad = math.radians(angle_deg)
        nx = cx + int(6 * math.cos(rad))
        ny = cy + int(6 * math.sin(rad))
        pygame.draw.line(s, c, (cx + int(4 * math.cos(rad)), cy + int(4 * math.sin(rad))), (nx, ny), 2)


_ICON_DISPATCH = {
    "fighter": _draw_fighter,
    "mage": _draw_mage,
    "cleric": _draw_cleric,
    "barbarian": _draw_barbarian,
    "paladin": _draw_paladin,
    "ranger": _draw_ranger,
    "monk": _draw_monk,
    "sorcerer": _draw_sorcerer,
    "warlock": _draw_warlock,
    "druid": _draw_druid,
    "rogue": _draw_rogue,
    "bard": _draw_bard,
    "artificer": _draw_artificer,
}
