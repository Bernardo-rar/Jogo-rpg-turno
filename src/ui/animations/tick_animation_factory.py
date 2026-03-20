"""Cria animacoes para ticks de efeitos (DoTs, regens)."""

from __future__ import annotations

from typing import Any

from src.core.combat.effect_phase import EffectLogEntry
from src.ui import colors
from src.ui.animations.floating_text import FloatingText
from src.ui.animations.heal_particles import HealParticles
from src.ui.animations.poison_bubbles import PoisonBubbles

DAMAGE_KEYWORD = "damage"
HEAL_KEYWORD = "heal"

_Rect = tuple[int, int, int, int]


def create_tick_animations(
    entry: EffectLogEntry, rect: _Rect,
) -> list[Any]:
    """Cria animacoes para um tick de efeito."""
    if entry.is_skip or entry.value == 0:
        return []
    if DAMAGE_KEYWORD in entry.message:
        return _tick_damage(entry, rect)
    if HEAL_KEYWORD in entry.message:
        return _tick_heal(entry, rect)
    return []


def _tick_damage(entry: EffectLogEntry, rect: _Rect) -> list[Any]:
    x, y, w, h = rect
    return [
        PoisonBubbles(x=x, y=y, width=w, height=h),
        FloatingText(f"-{entry.value}", x=x + w // 2, y=y, color=colors.TEXT_DAMAGE),
    ]


def _tick_heal(entry: EffectLogEntry, rect: _Rect) -> list[Any]:
    x, y, w, h = rect
    return [
        HealParticles(x=x, y=y, width=w, height=h),
        FloatingText(f"+{entry.value}", x=x + w // 2, y=y, color=colors.TEXT_HEAL),
    ]
