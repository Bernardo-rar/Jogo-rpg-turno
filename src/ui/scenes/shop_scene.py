"""ShopScene — tela de loja com abas de compra e venda."""

from __future__ import annotations

from enum import Enum, auto
from typing import Callable

import pygame

from src.dungeon.shop.shop_state import ShopState
from src.ui import colors, layout
from src.ui.components.confirm_dialog import ConfirmDialog
from src.ui.font_manager import FontManager

_SHOP_COLOR = (80, 180, 200)
_LINE_HEIGHT = 30
_MAX_VISIBLE = 8


class _Tab(Enum):
    BUY = auto()
    SELL = auto()


class ShopScene:
    """Tela de loja: comprar e vender itens."""

    def __init__(
        self,
        fonts: FontManager,
        shop: ShopState,
        on_buy: Callable[[int], bool],
        on_sell: Callable[[int], int],
        gold_getter: Callable[[], int],
        loot_getter: Callable[[], list],
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._shop = shop
        self._on_buy = on_buy
        self._on_sell = on_sell
        self._gold_getter = gold_getter
        self._loot_getter = loot_getter
        self._on_complete = on_complete
        self._tab = _Tab.BUY
        self._cursor: int = 0
        self._message: str = ""
        self._confirm: ConfirmDialog | None = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if self._confirm is not None:
            self._confirm.handle_key(key)
            if self._confirm.is_done:
                if self._confirm.confirmed:
                    self._on_complete({})
                self._confirm = None
            return
        if key == pygame.K_ESCAPE:
            self._confirm = ConfirmDialog("Sair da loja?")
            return
        if key == pygame.K_TAB:
            self._toggle_tab()
        elif key in (pygame.K_UP, pygame.K_w):
            self._move_cursor(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._move_cursor(1)
        elif key == pygame.K_RETURN:
            self._confirm_action()
        else:
            self._handle_item_key(event.key)

    def _toggle_tab(self) -> None:
        """Alterna entre abas BUY e SELL."""
        if self._tab == _Tab.BUY:
            self._tab = _Tab.SELL
        else:
            self._tab = _Tab.BUY
        self._cursor = 0
        self._message = ""

    def _move_cursor(self, delta: int) -> None:
        count = self._item_count()
        if count == 0:
            return
        self._cursor = max(0, min(count - 1, self._cursor + delta))

    def _item_count(self) -> int:
        if self._tab == _Tab.BUY:
            return len(self._shop.items)
        return len(self._loot_getter())

    def _confirm_action(self) -> None:
        """Enter compra/vende o item no cursor."""
        if self._tab == _Tab.BUY:
            self._try_buy(self._cursor)
        else:
            self._try_sell(self._cursor)

    def _handle_item_key(self, key: int) -> None:
        """Processa tecla numerica para compra/venda."""
        idx = _key_to_index(key)
        if idx is None:
            return
        if self._tab == _Tab.BUY:
            self._try_buy(idx)
        else:
            self._try_sell(idx)

    def _try_buy(self, index: int) -> None:
        """Tenta comprar item no indice."""
        if index >= len(self._shop.items):
            return
        if self._on_buy(index):
            item = self._shop.items[index]
            self._message = f"Comprou {item.name}!"
        else:
            self._message = "Sem gold ou fora de estoque!"

    def _try_sell(self, index: int) -> None:
        """Tenta vender item do inventario."""
        earned = self._on_sell(index)
        if earned > 0:
            self._message = f"Vendeu por {earned} gold!"
        else:
            self._message = "Nada para vender!"

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        cx = layout.WINDOW_WIDTH // 2
        _centered(surface, self._fonts.large, "Loja", cx, 60, _SHOP_COLOR)
        _draw_gold_bar(surface, self._fonts, self._gold_getter())
        _draw_tabs(surface, self._fonts, cx, self._tab)
        if self._tab == _Tab.BUY:
            _draw_buy_list(surface, self._fonts, self._shop, self._cursor)
        else:
            _draw_sell_list(surface, self._fonts, self._loot_getter(), self._cursor)
        if self._message:
            _centered(surface, self._fonts.small, self._message, cx, 600, colors.TEXT_YELLOW)
        _draw_controls(surface, self._fonts, cx)
        if self._confirm is not None:
            self._confirm.draw(surface, self._fonts.medium)


def _draw_gold_bar(
    surface: pygame.Surface,
    fonts: FontManager,
    gold: int,
) -> None:
    """Desenha total de gold no topo."""
    text = fonts.medium.render(f"Gold: {gold}", True, colors.TEXT_YELLOW)
    surface.blit(text, (40, 100))


def _draw_tabs(
    surface: pygame.Surface,
    fonts: FontManager,
    cx: int,
    active: _Tab,
) -> None:
    """Desenha indicadores de aba."""
    buy_color = colors.TEXT_YELLOW if active == _Tab.BUY else colors.TEXT_MUTED
    sell_color = colors.TEXT_YELLOW if active == _Tab.SELL else colors.TEXT_MUTED
    buy_text = fonts.medium.render("[ COMPRAR ]", True, buy_color)
    sell_text = fonts.medium.render("[ VENDER ]", True, sell_color)
    surface.blit(buy_text, (cx - 200, 140))
    surface.blit(sell_text, (cx + 50, 140))


def _draw_buy_list(
    surface: pygame.Surface,
    fonts: FontManager,
    shop: ShopState,
    cursor: int = 0,
) -> None:
    """Desenha lista de itens para compra com cursor."""
    y = 200
    visible = shop.items[:_MAX_VISIBLE]
    for i, item in enumerate(visible):
        stock_str = f"x{item.stock}" if item.stock > 0 else "ESGOTADO"
        selected = i == cursor
        available = item.stock > 0
        color = colors.TEXT_YELLOW if selected else (
            colors.TEXT_WHITE if available else colors.TEXT_MUTED
        )
        prefix = ">" if selected else " "
        label = f"{prefix}[{i + 1}] {item.name} - {item.price}g ({stock_str})"
        text = fonts.small.render(label, True, color)
        surface.blit(text, (100, y + i * _LINE_HEIGHT))


def _draw_sell_list(
    surface: pygame.Surface,
    fonts: FontManager,
    loot: list,
    cursor: int = 0,
) -> None:
    """Desenha lista de itens para venda com cursor."""
    y = 200
    if not loot:
        text = fonts.small.render("Nenhum item para vender.", True, colors.TEXT_MUTED)
        surface.blit(text, (100, y))
        return
    visible = loot[:_MAX_VISIBLE]
    for i, drop in enumerate(visible):
        name = drop.item_id.replace("_", " ").title()
        selected = i == cursor
        color = colors.TEXT_YELLOW if selected else colors.TEXT_WHITE
        prefix = ">" if selected else " "
        label = f"{prefix}[{i + 1}] {name}"
        text = fonts.small.render(label, True, color)
        surface.blit(text, (100, y + i * _LINE_HEIGHT))


def _draw_controls(
    surface: pygame.Surface,
    fonts: FontManager,
    cx: int,
) -> None:
    """Desenha instrucoes de controle."""
    _centered(
        surface, fonts.small,
        "[W/S] Navegar   [ENTER] Comprar/Vender   [TAB] Aba   [ESC] Sair",
        cx, 650, colors.TEXT_MUTED,
    )


def _key_to_index(key: int) -> int | None:
    mapping = {
        pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
        pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
        pygame.K_7: 6, pygame.K_8: 7,
    }
    return mapping.get(key)


def _centered(surface, font, text, x, y, color):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)
