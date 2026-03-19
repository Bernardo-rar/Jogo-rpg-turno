"""Debug screenshot helper — salva frames do Pygame como PNG."""

from __future__ import annotations

import os
from pathlib import Path

import pygame

_DEBUG_DIR = Path("debug/screenshots")

_screenshot_counter = 0


def capture(surface: pygame.Surface, label: str = "") -> Path:
    """Salva a surface como PNG e retorna o path.

    Args:
        surface: Pygame surface para capturar.
        label: Nome descritivo (ex: 'menu_level2', 'after_attack').
               Se vazio, usa contador auto-incrementado.

    Returns:
        Path do arquivo salvo.
    """
    global _screenshot_counter  # noqa: PLW0603

    _DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    if label:
        filename = f"{label}.png"
    else:
        _screenshot_counter += 1
        filename = f"frame_{_screenshot_counter:04d}.png"

    path = _DEBUG_DIR / filename
    pygame.image.save(surface, str(path))
    return path


def capture_on_key(
    surface: pygame.Surface, event: pygame.event.Event,
    key: int = pygame.K_F12,
) -> Path | None:
    """Captura screenshot se a tecla de debug for pressionada.

    Args:
        surface: Pygame surface para capturar.
        event: Evento Pygame do input loop.
        key: Tecla que dispara a captura (default: F12).

    Returns:
        Path do arquivo se capturou, None caso contrario.
    """
    if event.type != pygame.KEYDOWN or event.key != key:
        return None
    return capture(surface, "")
