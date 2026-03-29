"""CombatRewardScene — tela de recompensas pos-combate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame

from src.dungeon.loot.drop_table import LootDrop
from src.ui import colors, layout
from src.ui.font_manager import FontManager

GOLD_COUNT_DURATION_MS = 1000
READY_DELAY_MS = 300
PANEL_WIDTH = 500
PANEL_HEIGHT = 400
PANEL_BORDER_RADIUS = 12
DROP_LINE_HEIGHT = 28
MAX_VISIBLE_DROPS = 8


@dataclass(frozen=True)
class RewardSceneConfig:
    """Agrupa parametros do CombatRewardScene."""

    gold_earned: int
    drops: tuple[LootDrop, ...]
    total_gold: int
    on_complete: Callable[[dict], None]


_LOOT_COLOR_MAP: dict[str, tuple[int, int, int]] = {
    "weapon": colors.LOOT_WEAPON,
    "armor": colors.LOOT_ARMOR,
    "accessory": colors.LOOT_ACCESSORY,
}


def color_for_item_type(
    item_type: str,
) -> tuple[int, int, int]:
    """Retorna cor baseada no item_type do drop."""
    return _LOOT_COLOR_MAP.get(item_type, colors.LOOT_CONSUMABLE)


def humanize_item_id(item_id: str) -> str:
    """Converte 'health_potion' em 'Health Potion'."""
    return item_id.replace("_", " ").title()


class CombatRewardScene:
    """Tela de recompensas com gold count-up e lista de drops."""

    def __init__(
        self,
        fonts: FontManager | None,
        gold_earned: int,
        drops: tuple[LootDrop, ...],
        total_gold: int,
        on_complete: Callable[[dict], None],
        xp_earned: int = 0,
        leveled_up: bool = False,
        new_level: int = 0,
    ) -> None:
        self._fonts = fonts
        self._config = RewardSceneConfig(
            gold_earned=gold_earned,
            drops=drops,
            total_gold=total_gold,
            on_complete=on_complete,
        )
        self._xp_earned = xp_earned
        self._leveled_up = leveled_up
        self._new_level = new_level
        self._gold_displayed: float = 0.0
        self._counting_done: bool = gold_earned == 0
        self._elapsed_ms: float = 0.0
        self._ready: bool = False

    @property
    def gold_displayed(self) -> int:
        """Gold atual exibido (arredondado)."""
        return int(self._gold_displayed)

    @property
    def counting_done(self) -> bool:
        """True quando a animacao de contagem terminou."""
        return self._counting_done

    def handle_event(self, event: pygame.event.Event) -> None:
        """Processa input do jogador."""
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._on_confirm()

    def _on_confirm(self) -> None:
        """Skip animacao ou confirma saida."""
        if not self._counting_done:
            self._skip_animation()
            return
        self._config.on_complete({})

    def _skip_animation(self) -> None:
        """Pula direto para o valor final."""
        self._gold_displayed = float(self._config.gold_earned)
        self._counting_done = True

    def update(self, dt_ms: int) -> bool:
        """Atualiza animacao de contagem de gold."""
        if not self._counting_done:
            self._update_gold_counter(dt_ms)
        return True

    def _update_gold_counter(self, dt_ms: int) -> None:
        """Incrementa gold_displayed ate atingir gold_earned."""
        self._elapsed_ms += dt_ms
        target = self._config.gold_earned
        progress = min(self._elapsed_ms / GOLD_COUNT_DURATION_MS, 1.0)
        self._gold_displayed = target * progress
        if progress >= 1.0:
            self._gold_displayed = float(target)
            self._counting_done = True

    def draw(self, surface: pygame.Surface) -> None:
        """Renderiza a tela de recompensas."""
        if self._fonts is None:
            return
        surface.fill(colors.BG_DARK)
        panel_rect = self._draw_panel(surface)
        self._draw_title(surface, panel_rect)
        self._draw_gold(surface, panel_rect)
        self._draw_xp(surface, panel_rect)
        self._draw_drops(surface, panel_rect)
        self._draw_total(surface, panel_rect)
        self._draw_prompt(surface, panel_rect)

    def _draw_panel(self, surface: pygame.Surface) -> pygame.Rect:
        """Desenha painel central com fundo e borda."""
        cx = layout.WINDOW_WIDTH // 2
        cy = layout.WINDOW_HEIGHT // 2
        rect = pygame.Rect(0, 0, PANEL_WIDTH, PANEL_HEIGHT)
        rect.center = (cx, cy)
        pygame.draw.rect(
            surface, colors.BG_PANEL, rect,
            border_radius=PANEL_BORDER_RADIUS,
        )
        pygame.draw.rect(
            surface, colors.BG_PANEL_BORDER, rect,
            width=2, border_radius=PANEL_BORDER_RADIUS,
        )
        return rect

    def _draw_title(
        self, surface: pygame.Surface, panel: pygame.Rect,
    ) -> None:
        """Desenha titulo 'Recompensas!' em amarelo."""
        _centered(
            surface, self._fonts.large,
            "Recompensas!", panel.centerx, panel.top + 35,
            colors.TEXT_YELLOW,
        )

    def _draw_gold(
        self, surface: pygame.Surface, panel: pygame.Rect,
    ) -> None:
        """Desenha gold earned com animacao de contagem."""
        text = f"Gold: {self.gold_displayed}"
        _centered(
            surface, self._fonts.medium,
            text, panel.centerx, panel.top + 80,
            colors.TEXT_YELLOW,
        )

    def _draw_xp(
        self, surface: pygame.Surface, panel: pygame.Rect,
    ) -> None:
        """Desenha XP earned e level up."""
        if self._xp_earned <= 0:
            return
        text = f"XP: +{self._xp_earned}"
        _centered(
            surface, self._fonts.medium,
            text, panel.centerx, panel.top + 105,
            (100, 200, 255),
        )
        if self._leveled_up:
            level_text = f"LEVEL UP! -> Lv.{self._new_level}"
            _centered(
                surface, self._fonts.medium,
                level_text, panel.centerx, panel.top + 130,
                colors.TEXT_YELLOW,
            )

    def _draw_drops(
        self, surface: pygame.Surface, panel: pygame.Rect,
    ) -> None:
        """Desenha lista de loot drops."""
        drops = self._config.drops
        if not drops:
            return
        y_start = panel.top + 160 if self._xp_earned > 0 else panel.top + 120
        _centered(
            surface, self._fonts.medium,
            "Loot:", panel.centerx, y_start,
            colors.TEXT_WHITE,
        )
        visible = drops[:MAX_VISIBLE_DROPS]
        for i, drop in enumerate(visible):
            name = humanize_item_id(drop.item_id)
            qty = f" x{drop.quantity}" if drop.quantity > 1 else ""
            drop_color = color_for_item_type(drop.item_type)
            _centered(
                surface, self._fonts.small,
                f"{name}{qty}", panel.centerx,
                y_start + 28 + i * DROP_LINE_HEIGHT,
                drop_color,
            )

    def _draw_total(
        self, surface: pygame.Surface, panel: pygame.Rect,
    ) -> None:
        """Desenha total de gold na run."""
        text = f"Gold total: {self._config.total_gold}"
        _centered(
            surface, self._fonts.medium,
            text, panel.centerx, panel.bottom - 70,
            colors.TEXT_MUTED,
        )

    def _draw_prompt(
        self, surface: pygame.Surface, panel: pygame.Rect,
    ) -> None:
        """Desenha prompt para continuar."""
        if not self._counting_done:
            return
        _centered(
            surface, self._fonts.small,
            "[ENTER] Continuar", panel.centerx, panel.bottom - 30,
            colors.TEXT_MUTED,
        )


def _centered(surface, font, text, x, y, color):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)
