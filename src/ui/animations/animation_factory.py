"""Dispatch table: EventType -> lista de animacoes."""

from __future__ import annotations

from typing import Any

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.elements.element_type import ElementType
from src.ui import colors
from src.ui.animations.buff_aura import BuffAura
from src.ui.animations.card_shake import CardShake
from src.ui.animations.element_colors import get_element_color
from src.ui.animations.floating_text import FloatingText
from src.ui.animations.heal_particles import HealParticles
from src.ui.animations.magic_burst import MagicBurst
from src.ui.animations.multi_slash import MultiSlash
from src.ui.animations.particle import ParticleConfig, ParticleEmitter
from src.ui.animations.particle_configs import (
    CELESTIAL_CONFIG, DARKNESS_CONFIG, EARTH_CONFIG,
    FIRE_CONFIG, FORCE_CONFIG, HOLY_CONFIG,
    ICE_CONFIG, LIGHTNING_CONFIG, PSYCHIC_CONFIG,
    WATER_CONFIG,
)
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
    if event.element is not None:
        return _create_magical_damage(event, rect, value)
    return _create_physical_damage(event, rect, value)


def _damage_text(event: CombatEvent, value: int, x: int, y: int) -> FloatingText:
    """Cria FloatingText de dano, com destaque visual para criticos."""
    is_crit = event.damage is not None and event.damage.is_critical
    text = f"-{value} CRIT!" if is_crit else f"-{value}"
    color = colors.TEXT_CRITICAL if is_crit else colors.TEXT_DAMAGE
    return FloatingText(text, x=x, y=y, color=color)


def _create_physical_damage(
    event: CombatEvent, rect: _Rect, value: int,
) -> list[Any]:
    x, y, w, h = rect
    return [
        MultiSlash(x=x, y=y, width=w, height=h),
        CardShake(target_name=event.target_name),
        _damage_text(event, value, x + w // 2, y),
    ]


def _create_magical_damage(
    event: CombatEvent, rect: _Rect, value: int,
) -> list[Any]:
    x, y, w, h = rect
    config = _ELEMENT_PARTICLES.get(event.element)
    if config is not None:
        return [
            ParticleEmitter(config, rect),
            _damage_text(event, value, x + w // 2, y),
        ]
    element_color = get_element_color(event.element)
    return [
        MagicBurst(cx=x + w // 2, cy=y + h // 2, color=element_color),
        _damage_text(event, value, x + w // 2, y),
    ]


_ELEMENT_PARTICLES: dict[ElementType | None, ParticleConfig] = {
    ElementType.FIRE: FIRE_CONFIG,
    ElementType.ICE: ICE_CONFIG,
    ElementType.LIGHTNING: LIGHTNING_CONFIG,
    ElementType.HOLY: HOLY_CONFIG,
    ElementType.DARKNESS: DARKNESS_CONFIG,
    ElementType.WATER: WATER_CONFIG,
    ElementType.EARTH: EARTH_CONFIG,
    ElementType.PSYCHIC: PSYCHIC_CONFIG,
    ElementType.FORCE: FORCE_CONFIG,
    ElementType.CELESTIAL: CELESTIAL_CONFIG,
}


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
