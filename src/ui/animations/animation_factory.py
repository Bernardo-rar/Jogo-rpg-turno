"""Dispatch table: EventType -> lista de animacoes."""

from __future__ import annotations

from typing import Any

from src.core.combat.combat_engine import CombatEvent, EventType
from src.ui import colors
from src.ui.animations.buff_aura import BuffAura
from src.ui.animations.card_shake import CardShake
from src.ui.animations.floating_text import FloatingText
from src.ui.animations.heal_particles import HealParticles
from src.ui.animations.poison_bubbles import PoisonBubbles
from src.ui.animations.slash_effect import SlashEffect

_Rect = tuple[int, int, int, int]


class AnimationFactory:
    """Cria animacoes a partir de eventos de combate."""

    def create(self, event: CombatEvent, target_rect: _Rect) -> list[Any]:
        """Retorna lista de animacoes para o evento."""
        handler = _DISPATCH.get(event.event_type)
        if handler is None:
            return []
        return handler(event, target_rect)


def _create_damage(event: CombatEvent, rect: _Rect) -> list[Any]:
    x, y, w, h = rect
    value = event.damage.final_damage if event.damage else event.value
    return [
        SlashEffect(x=x, y=y, width=w, height=h),
        CardShake(target_name=event.target_name),
        FloatingText(
            f"-{value}", x=x + w // 2, y=y,
            color=colors.TEXT_DAMAGE,
        ),
    ]


def _create_heal(event: CombatEvent, rect: _Rect) -> list[Any]:
    x, y, w, h = rect
    return [
        HealParticles(x=x, y=y, width=w, height=h),
        FloatingText(
            f"+{event.value}", x=x + w // 2, y=y,
            color=colors.TEXT_HEAL,
        ),
    ]


def _create_buff(event: CombatEvent, rect: _Rect) -> list[Any]:
    x, y, w, h = rect
    return [BuffAura(x=x, y=y, width=w, height=h, color=colors.EFFECT_BUFF)]


def _create_debuff(event: CombatEvent, rect: _Rect) -> list[Any]:
    x, y, w, h = rect
    return [BuffAura(x=x, y=y, width=w, height=h, color=colors.EFFECT_DEBUFF)]


def _create_ailment(event: CombatEvent, rect: _Rect) -> list[Any]:
    x, y, w, h = rect
    return [PoisonBubbles(x=x, y=y, width=w, height=h)]


_DISPATCH: dict[EventType, Any] = {
    EventType.DAMAGE: _create_damage,
    EventType.HEAL: _create_heal,
    EventType.BUFF: _create_buff,
    EventType.DEBUFF: _create_debuff,
    EventType.AILMENT: _create_ailment,
}
