"""Tooltip de descricao de skill no menu SPECIFIC_ACTION."""

from __future__ import annotations

import pygame

from src.core.skills.skill import Skill
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.ui import layout

# -- cores do tooltip --
_CLR_NAME = (255, 255, 255)
_CLR_DESC = (180, 180, 180)
_CLR_MANA = (100, 150, 255)
_CLR_RESOURCE = (255, 180, 50)
_CLR_DAMAGE = (255, 80, 80)
_CLR_HEAL = (80, 255, 80)
_CLR_BUFF = (80, 255, 255)
_CLR_DEBUFF = (255, 255, 80)
_CLR_AILMENT = (200, 100, 255)
_CLR_SHIELD = (150, 200, 255)
_CLR_COOLDOWN = (150, 150, 150)
_CLR_ELEMENT = (200, 200, 255)
_CLR_GRANT = (255, 255, 255)

# -- dimensoes --
_TOOLTIP_WIDTH = 250
_TOOLTIP_PADDING = 8
_LINE_HEIGHT = 18
_BORDER_RADIUS = 6
_BG_COLOR = (20, 20, 35, 230)
_BORDER_COLOR = (80, 80, 120)
_GAP_FROM_PANEL = 10

# -- nomes de recurso --
_RESOURCE_DISPLAY: dict[str, str] = {
    "fury_bar": "Fury",
    "holy_power": "Holy",
    "action_points": "AP",
    "insanity_bar": "Insanity",
    "equilibrium_bar": "Equilibrium",
    "groove": "Groove",
}

# -- tipo info por SkillEffectType --
SkillLine = tuple[str, tuple[int, int, int]]


def build_skill_info_lines(
    skill: Skill, caster: object,
) -> list[SkillLine]:
    """Monta linhas de tooltip a partir de Skill + caster."""
    lines: list[SkillLine] = [(skill.name, _CLR_NAME)]
    if skill.description:
        lines.append((skill.description, _CLR_DESC))
    _append_cost_lines(lines, skill)
    _append_effect_lines(lines, skill, caster)
    _append_meta_lines(lines, skill)
    return lines


def draw_skill_tooltip(
    surface: pygame.Surface, skill: Skill,
    caster: object, font: pygame.font.Font,
) -> None:
    """Desenha tooltip de skill ao lado direito do action panel."""
    lines = build_skill_info_lines(skill, caster)
    x = layout.ACTION_PANEL_X + layout.ACTION_PANEL_WIDTH + _GAP_FROM_PANEL
    y = layout.ACTION_PANEL_Y
    _render_tooltip(surface, lines, x, y, font)


# -- funcoes internas de montagem de linhas --


def _append_cost_lines(
    lines: list[SkillLine], skill: Skill,
) -> None:
    """Adiciona linhas de custo (mana + recursos de classe)."""
    if skill.mana_cost > 0:
        lines.append((f"Mana: {skill.mana_cost}", _CLR_MANA))
    for rc in skill.resource_costs:
        name = _RESOURCE_DISPLAY.get(rc.resource_type, rc.resource_type)
        lines.append((f"{name}: {rc.amount}", _CLR_RESOURCE))


def _append_effect_lines(
    lines: list[SkillLine], skill: Skill, caster: object,
) -> None:
    """Adiciona linhas para cada efeito da skill."""
    for effect in skill.effects:
        line = _effect_to_line(effect, caster)
        if line is not None:
            lines.append(line)


def _append_meta_lines(
    lines: list[SkillLine], skill: Skill,
) -> None:
    """Adiciona cooldown e elemento se existirem."""
    if skill.cooldown_turns > 0:
        lines.append((f"Cooldown: {skill.cooldown_turns} turns", _CLR_COOLDOWN))
    element = _first_element(skill)
    if element is not None:
        lines.append((f"Element: {element.name.title()}", _CLR_ELEMENT))


def _effect_to_line(
    effect: SkillEffect, caster: object,
) -> SkillLine | None:
    """Converte um SkillEffect em linha de tooltip."""
    builder = _EFFECT_LINE_MAP.get(effect.effect_type)
    if builder is None:
        return None
    return builder(effect, caster)


def _damage_line(effect: SkillEffect, caster: object) -> SkillLine:
    estimate = _estimate_damage(effect, caster)
    return (f"Damage: ~{estimate}", _CLR_DAMAGE)


def _heal_line(effect: SkillEffect, caster: object) -> SkillLine:
    estimate = _estimate_heal(effect, caster)
    return (f"Heal: ~{estimate}", _CLR_HEAL)


def _buff_line(effect: SkillEffect, _caster: object) -> SkillLine:
    stat_name = effect.stat.name.title() if effect.stat else "?"
    dur = f" ({effect.duration} turns)" if effect.duration else ""
    return (f"+{effect.base_power} {stat_name}{dur}", _CLR_BUFF)


def _debuff_line(effect: SkillEffect, _caster: object) -> SkillLine:
    stat_name = effect.stat.name.title() if effect.stat else "?"
    dur = f" ({effect.duration} turns)" if effect.duration else ""
    return (f"-{effect.base_power} {stat_name}{dur}", _CLR_DEBUFF)


def _ailment_line(effect: SkillEffect, _caster: object) -> SkillLine:
    ailment = effect.ailment_id or "unknown"
    return (f"Applies: {ailment}", _CLR_AILMENT)


def _shield_line(effect: SkillEffect, _caster: object) -> SkillLine:
    return (f"Shield: {effect.base_power}", _CLR_SHIELD)


_EFFECT_LINE_MAP = {
    SkillEffectType.DAMAGE: _damage_line,
    SkillEffectType.HEAL: _heal_line,
    SkillEffectType.BUFF: _buff_line,
    SkillEffectType.DEBUFF: _debuff_line,
    SkillEffectType.APPLY_AILMENT: _ailment_line,
    SkillEffectType.SHIELD: _shield_line,
}


def _estimate_damage(effect: SkillEffect, caster: object) -> int:
    """Estimativa simples de dano: base_power + ataque do caster."""
    atk = getattr(caster, "magical_attack", 0)
    if effect.element is None:
        atk = getattr(caster, "physical_attack", atk)
    return effect.base_power + atk


def _estimate_heal(effect: SkillEffect, caster: object) -> int:
    """Estimativa simples de cura: base_power + magical_attack."""
    return effect.base_power + getattr(caster, "magical_attack", 0)


def _first_element(skill: Skill) -> object | None:
    """Retorna o primeiro elemento encontrado nos efeitos."""
    for eff in skill.effects:
        if eff.element is not None:
            return eff.element
    return None


# -- renderizacao --


def _render_tooltip(
    surface: pygame.Surface,
    lines: list[SkillLine],
    x: int, y: int,
    font: pygame.font.Font,
) -> None:
    """Renderiza o tooltip com fundo semi-transparente."""
    height = _TOOLTIP_PADDING * 2 + len(lines) * _LINE_HEIGHT
    y = _clamp_y(y, height)
    _draw_background(surface, x, y, height)
    _draw_lines(surface, lines, x, y, font)


def _clamp_y(y: int, height: int) -> int:
    """Garante que o tooltip nao ultrapasse a borda inferior."""
    max_y = layout.WINDOW_HEIGHT - height - 4
    return min(y, max_y)


def _draw_background(
    surface: pygame.Surface, x: int, y: int, height: int,
) -> None:
    """Desenha fundo e borda do tooltip."""
    bg = pygame.Surface((_TOOLTIP_WIDTH, height), pygame.SRCALPHA)
    bg.fill(_BG_COLOR)
    surface.blit(bg, (x, y))
    rect = pygame.Rect(x, y, _TOOLTIP_WIDTH, height)
    pygame.draw.rect(surface, _BORDER_COLOR, rect, 1, _BORDER_RADIUS)


def _draw_lines(
    surface: pygame.Surface,
    lines: list[SkillLine],
    x: int, y: int,
    font: pygame.font.Font,
) -> None:
    """Renderiza cada linha de texto."""
    tx = x + _TOOLTIP_PADDING
    ty = y + _TOOLTIP_PADDING
    for text, color in lines:
        rendered = font.render(text, True, color)
        surface.blit(rendered, (tx, ty))
        ty += _LINE_HEIGHT
