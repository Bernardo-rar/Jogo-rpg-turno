"""EquipmentScene — tela de gerenciamento de equipamento (3 paineis)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, TYPE_CHECKING

import pygame

from src.core.items.accessory import Accessory
from src.core.items.armor import Armor
from src.core.items.weapon import Weapon
from src.dungeon.loot.drop_table import LootDrop
from src.dungeon.run.equipment_catalog import EquipmentCatalogs
from src.ui import colors, layout
from src.ui.font_manager import FontManager

if TYPE_CHECKING:
    from src.core.characters.character import Character

_PANEL_LEFT_W = 250
_PANEL_CENTER_W = 450
_PANEL_RIGHT_W = 350
_PANEL_TOP = 80
_LINE_H = 30
_SLOT_NAMES = ("Weapon", "Armor", "Accessory 1", "Accessory 2")
_SLOT_COUNT = 4
_MAX_STASH_VISIBLE = 12
_STAT_NAMES = ("ATK", "MATK", "PDEF", "MDEF", "SPD", "HP", "AC")

_COLOR_POSITIVE = colors.TEXT_HEAL
_COLOR_NEGATIVE = colors.TEXT_DAMAGE
_COLOR_NEUTRAL = colors.TEXT_MUTED
_COLOR_SELECTED = colors.TEXT_YELLOW
_COLOR_HEADER = colors.PARTY_COLOR


class _Focus(Enum):
    PARTY = auto()
    SLOTS = auto()
    STASH = auto()


@dataclass(frozen=True)
class StatDiff:
    """Uma linha de preview de stat."""

    stat_name: str
    old_value: int
    new_value: int

    @property
    def delta(self) -> int:
        return self.new_value - self.old_value


@dataclass(frozen=True)
class _PanelState:
    """Estado de selecao de um painel para renderizacao."""

    is_active: bool
    selected_index: int
    scroll_offset: int = 0


@dataclass
class _EquipContext:
    """Contexto mutavel para operacoes de equip/unequip."""

    stash: list[LootDrop]
    catalogs: EquipmentCatalogs


class EquipmentScene:
    """Tela de equipamento com 3 paineis: party, slots, stash."""

    def __init__(
        self,
        fonts: FontManager | None,
        party: list[Character],
        equipment_stash: list[LootDrop],
        catalogs: EquipmentCatalogs,
        on_complete: Callable[[dict], None],
        gold: int = 0,
    ) -> None:
        self._fonts = fonts
        self._party = party
        self._stash = equipment_stash
        self._catalogs = catalogs
        self._ctx = _EquipContext(stash=equipment_stash, catalogs=catalogs)
        self._on_complete = on_complete
        self._gold = gold
        self._focus = _Focus.PARTY
        self._party_index = 0
        self._slot_index = 0
        self._stash_index = 0
        self._stash_scroll = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        handler = _KEY_HANDLERS.get(event.key)
        if handler is not None:
            handler(self)
            return
        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self._on_complete({})

    def _cycle_focus(self) -> None:
        """Cicla foco para direita: PARTY -> SLOTS -> STASH -> PARTY."""
        order = [_Focus.PARTY, _Focus.SLOTS, _Focus.STASH]
        idx = order.index(self._focus)
        self._focus = order[(idx + 1) % len(order)]

    def _cycle_focus_back(self) -> None:
        """Cicla foco para esquerda: PARTY -> STASH -> SLOTS -> PARTY."""
        order = [_Focus.PARTY, _Focus.SLOTS, _Focus.STASH]
        idx = order.index(self._focus)
        self._focus = order[(idx - 1) % len(order)]

    def _navigate(self, direction: int) -> None:
        """Move selecao no painel ativo. direction: -1=up, +1=down."""
        if self._focus == _Focus.PARTY:
            limit = len(self._party) - 1
            self._party_index = _clamp(self._party_index + direction, 0, limit)
        elif self._focus == _Focus.SLOTS:
            self._slot_index = _clamp(self._slot_index + direction, 0, _SLOT_COUNT - 1)
        elif self._focus == _Focus.STASH:
            limit = max(0, len(self._stash) - 1)
            self._stash_index = _clamp(self._stash_index + direction, 0, limit)
            _adjust_scroll(self)

    def _handle_confirm(self) -> None:
        """ENTER: equip do stash ou unequip do slot."""
        if self._focus == _Focus.STASH and self._stash:
            self.equip_from_stash(
                self._party_index, self._slot_index, self._stash_index,
            )
        elif self._focus == _Focus.SLOTS:
            self.unequip_slot(self._party_index, self._slot_index)

    def equip_from_stash(
        self, char_index: int, slot_index: int, stash_index: int,
    ) -> None:
        """Equipa item do stash no slot do personagem."""
        if stash_index >= len(self._stash):
            return
        drop = self._stash[stash_index]
        item = self._catalogs.resolve_drop(drop)
        if item is None:
            return
        char = self._party[char_index]
        _apply_equip(char, item, slot_index, self._ctx)
        _remove_drop(self._stash, stash_index)
        self._clamp_stash_index()

    def unequip_slot(self, char_index: int, slot_index: int) -> None:
        """Remove item do slot e devolve ao stash."""
        char = self._party[char_index]
        _apply_unequip(char, slot_index, self._ctx)

    def _clamp_stash_index(self) -> None:
        if not self._stash:
            self._stash_index = 0
            return
        limit = len(self._stash) - 1
        self._stash_index = min(self._stash_index, limit)

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        if self._fonts is None:
            return
        _draw_title(surface, self._fonts)
        _draw_gold(surface, self._fonts, self._gold)
        party_ps = _PanelState(
            self._focus == _Focus.PARTY, self._party_index,
        )
        _draw_party_panel(surface, self._fonts, self._party, party_ps)
        slot_ps = _PanelState(
            self._focus == _Focus.SLOTS, self._slot_index,
        )
        char = self._party[self._party_index]
        _draw_slots_panel(surface, self._fonts, char, slot_ps)
        stash_view = _StashView(
            stash=self._stash,
            panel_state=_PanelState(
                self._focus == _Focus.STASH, self._stash_index, self._stash_scroll,
            ),
            catalogs=self._catalogs,
        )
        _draw_stash_panel(surface, self._fonts, stash_view)
        self._draw_stat_preview(surface)
        _draw_controls(surface, self._fonts)

    def _draw_stat_preview(self, surface: pygame.Surface) -> None:
        """Desenha preview de stats se stash tem item selecionado."""
        if not self._stash or self._focus != _Focus.STASH:
            return
        drop = self._stash[self._stash_index]
        item = self._catalogs.resolve_drop(drop)
        if item is None:
            return
        char = self._party[self._party_index]
        preview = compute_stat_preview(
            char, item, self._slot_index, self._catalogs,
        )
        y = layout.WINDOW_HEIGHT - 140
        header = self._fonts.medium.render(
            "Stat Preview:", True, colors.TEXT_WHITE,
        )
        surface.blit(header, (20, y))
        y += 24
        _draw_stat_diff_lines(surface, self._fonts, preview, y)


def _clamp(value: int, low: int, high: int) -> int:
    """Restringe valor entre low e high."""
    return max(low, min(value, high))


def _adjust_scroll(scene: EquipmentScene) -> None:
    """Mantem stash_index visivel na janela de scroll."""
    if scene._stash_index < scene._stash_scroll:
        scene._stash_scroll = scene._stash_index
    visible_end = scene._stash_scroll + _MAX_STASH_VISIBLE
    if scene._stash_index >= visible_end:
        scene._stash_scroll = scene._stash_index - _MAX_STASH_VISIBLE + 1


_DIRECTION_UP = -1
_DIRECTION_DOWN = 1

_KEY_HANDLERS: dict[int, object] = {
    pygame.K_RIGHT: EquipmentScene._cycle_focus,
    pygame.K_d: EquipmentScene._cycle_focus,
    pygame.K_LEFT: EquipmentScene._cycle_focus_back,
    pygame.K_a: EquipmentScene._cycle_focus_back,
    pygame.K_UP: lambda s: s._navigate(_DIRECTION_UP),
    pygame.K_w: lambda s: s._navigate(_DIRECTION_UP),
    pygame.K_DOWN: lambda s: s._navigate(_DIRECTION_DOWN),
    pygame.K_s: lambda s: s._navigate(_DIRECTION_DOWN),
    pygame.K_RETURN: EquipmentScene._handle_confirm,
}


def _draw_party_panel(
    surface: pygame.Surface,
    fonts: FontManager,
    party: list[Character],
    ps: _PanelState,
) -> None:
    _draw_panel_header(surface, fonts, 20, "Party")
    for i, char in enumerate(party):
        selected = ps.is_active and i == ps.selected_index
        color = _COLOR_SELECTED if selected else colors.TEXT_WHITE
        label = f"  {char.name}"
        y = _PANEL_TOP + 30 + i * _LINE_H
        text = fonts.small.render(label, True, color)
        surface.blit(text, (20, y))


def _draw_slots_panel(
    surface: pygame.Surface,
    fonts: FontManager,
    char: Character,
    ps: _PanelState,
) -> None:
    x = _PANEL_LEFT_W + 20
    _draw_panel_header(surface, fonts, x, "Slots")
    for i in range(_SLOT_COUNT):
        name = _get_slot_item_name(char, i)
        selected = ps.is_active and i == ps.selected_index
        color = _COLOR_SELECTED if selected else colors.TEXT_WHITE
        label = f"  {_SLOT_NAMES[i]}: {name}"
        y = _PANEL_TOP + 30 + i * _LINE_H
        text = fonts.small.render(label, True, color)
        surface.blit(text, (x, y))


@dataclass(frozen=True)
class _StashView:
    """Dados necessarios para renderizar o painel de stash."""

    stash: list[LootDrop]
    panel_state: _PanelState
    catalogs: EquipmentCatalogs


def _drop_label(drop: LootDrop, catalogs: EquipmentCatalogs) -> str:
    """Formata label de um LootDrop para exibicao."""
    item = catalogs.resolve_drop(drop)
    name = item.name if item else drop.item_id
    return f"  [{drop.item_type[0].upper()}] {name}"


def _draw_stash_panel(
    surface: pygame.Surface, fonts: FontManager, view: _StashView,
) -> None:
    x = _PANEL_LEFT_W + _PANEL_CENTER_W + 20
    _draw_panel_header(surface, fonts, x, "Stash")
    if not view.stash:
        empty = fonts.small.render("  (empty)", True, _COLOR_NEUTRAL)
        surface.blit(empty, (x, _PANEL_TOP + 30))
        return
    ps = view.panel_state
    end = ps.scroll_offset + _MAX_STASH_VISIBLE
    for i, drop in enumerate(view.stash[ps.scroll_offset:end]):
        selected = ps.is_active and (ps.scroll_offset + i) == ps.selected_index
        color = _COLOR_SELECTED if selected else colors.TEXT_WHITE
        label = _drop_label(drop, view.catalogs)
        text = fonts.small.render(label, True, color)
        surface.blit(text, (x, _PANEL_TOP + 30 + i * _LINE_H))


def compute_stat_preview(
    char: Character,
    item: Weapon | Armor | Accessory,
    slot_index: int,
    catalogs: EquipmentCatalogs,
) -> tuple[StatDiff, ...]:
    """Calcula diff de stats se item fosse equipado."""
    old_stats = _snapshot_stats(char)
    saved = _save_and_equip(char, item, slot_index)
    new_stats = _snapshot_stats(char)
    _restore_slot(char, saved, slot_index)
    return _build_diffs(old_stats, new_stats)


def _snapshot_stats(char: Character) -> dict[str, int]:
    """Captura stats atuais do personagem."""
    return {
        "ATK": char.physical_attack,
        "MATK": char.magical_attack,
        "PDEF": char.physical_defense,
        "MDEF": char.magical_defense,
        "SPD": char.speed,
        "HP": char.max_hp,
        "AC": char.armor_class,
    }


def _save_and_equip(
    char: Character, item: Weapon | Armor | Accessory, slot_index: int,
) -> Weapon | Armor | None:
    """Equipa item temporariamente, retorna o antigo."""
    if slot_index == 0 and isinstance(item, Weapon):
        old = char.unequip_weapon()
        char.equip_weapon(item)
        return old
    if slot_index == 1 and isinstance(item, Armor):
        old = char.unequip_armor()
        char.equip_armor(item)
        return old
    return None


def _restore_slot(
    char: Character, old: Weapon | Armor | None, slot_index: int,
) -> None:
    """Restaura item antigo no slot."""
    if slot_index == 0:
        char.unequip_weapon()
        if isinstance(old, Weapon):
            char.equip_weapon(old)
    elif slot_index == 1:
        char.unequip_armor()
        if isinstance(old, Armor):
            char.equip_armor(old)


def _build_diffs(
    old: dict[str, int], new: dict[str, int],
) -> tuple[StatDiff, ...]:
    """Cria tuple de StatDiff a partir de snapshots."""
    return tuple(
        StatDiff(stat_name=name, old_value=old[name], new_value=new[name])
        for name in _STAT_NAMES
        if old[name] != new[name]
    )


def _draw_stat_diff_lines(
    surface: pygame.Surface,
    fonts: FontManager,
    diffs: tuple[StatDiff, ...],
    start_y: int,
) -> None:
    """Desenha linhas de diff de stats."""
    y = start_y
    for diff in diffs:
        sign = "+" if diff.delta > 0 else ""
        color = _COLOR_POSITIVE if diff.delta > 0 else _COLOR_NEGATIVE
        label = f"  {diff.stat_name}: {diff.old_value} -> {diff.new_value} ({sign}{diff.delta})"
        text = fonts.small.render(label, True, color)
        surface.blit(text, (20, y))
        y += 20


def _apply_equip(
    char: Character, item: object, slot_index: int, ctx: _EquipContext,
) -> None:
    """Roteia equip para o slot correto."""
    if slot_index == 0:
        _equip_weapon(char, item, ctx)
    elif slot_index == 1:
        _equip_armor(char, item, ctx)
    else:
        _equip_accessory(char, item, ctx)


def _apply_unequip(
    char: Character, slot_index: int, ctx: _EquipContext,
) -> None:
    """Roteia unequip para o slot correto."""
    if slot_index == 0:
        _unequip_weapon(char, ctx)
    elif slot_index == 1:
        _unequip_armor(char, ctx)
    else:
        _unequip_accessory(char, slot_index - 2, ctx)


def _equip_weapon(char: Character, item: object, ctx: _EquipContext) -> None:
    """Equipa weapon, devolvendo a antiga ao stash."""
    if not isinstance(item, Weapon):
        return
    old = char.unequip_weapon()
    if old is not None:
        _return_to_stash("weapon", old, ctx)
    char.equip_weapon(item)


def _equip_armor(char: Character, item: object, ctx: _EquipContext) -> None:
    """Equipa armor, devolvendo a antiga ao stash."""
    if not isinstance(item, Armor):
        return
    old = char.unequip_armor()
    if old is not None:
        _return_to_stash("armor", old, ctx)
    char.equip_armor(item)


def _equip_accessory(char: Character, item: object, ctx: _EquipContext) -> None:
    """Equipa accessory, devolvendo o antigo ao stash se slot cheio."""
    if not isinstance(item, Accessory):
        return
    success = char.equip_accessory(item)
    if not success:
        accs = char.accessories
        if accs:
            old = accs[-1]
            char.unequip_accessory(old)
            _return_to_stash("accessory", old, ctx)
            char.equip_accessory(item)


def _unequip_weapon(char: Character, ctx: _EquipContext) -> None:
    """Remove weapon e devolve ao stash."""
    old = char.unequip_weapon()
    if old is not None:
        _return_to_stash("weapon", old, ctx)


def _unequip_armor(char: Character, ctx: _EquipContext) -> None:
    """Remove armor e devolve ao stash."""
    old = char.unequip_armor()
    if old is not None:
        _return_to_stash("armor", old, ctx)


def _unequip_accessory(char: Character, acc_index: int, ctx: _EquipContext) -> None:
    """Remove accessory pelo indice e devolve ao stash."""
    accs = char.accessories
    if acc_index >= len(accs):
        return
    old = accs[acc_index]
    char.unequip_accessory(old)
    _return_to_stash("accessory", old, ctx)


def _return_to_stash(item_type: str, item: object, ctx: _EquipContext) -> None:
    """Devolve item ao stash como LootDrop."""
    item_id = _find_item_id(item_type, item, ctx.catalogs)
    if item_id is None:
        item_id = _fallback_item_id(item)
    ctx.stash.append(LootDrop(item_type=item_type, item_id=item_id))


def _find_item_id(
    item_type: str, item: object, catalogs: EquipmentCatalogs,
) -> str | None:
    """Busca item_id no catalogo apropriado."""
    if item_type == "weapon":
        return catalogs.find_weapon_id(item)
    if item_type == "armor":
        return catalogs.find_armor_id(item)
    if item_type == "accessory":
        return catalogs.find_accessory_id(item)
    return None


def _fallback_item_id(item: object) -> str:
    """Gera item_id a partir do nome do item."""
    name = getattr(item, "name", "unknown")
    return name.lower().replace(" ", "_")


def _get_slot_item_name(char: Character, slot_index: int) -> str:
    """Retorna nome do item no slot ou 'Empty'."""
    if slot_index == 0:
        return char.weapon.name if char.weapon else "Empty"
    if slot_index == 1:
        return char.armor.name if char.armor else "Empty"
    acc_idx = slot_index - 2
    accs = char.accessories
    if acc_idx < len(accs):
        return accs[acc_idx].name
    return "Empty"


def _remove_drop(stash: list[LootDrop], index: int) -> None:
    """Remove drop do stash pelo indice."""
    if index < len(stash):
        stash.pop(index)


def _draw_title(
    surface: pygame.Surface, fonts: FontManager,
) -> None:
    title = fonts.large.render("Equipment", True, colors.TEXT_WHITE)
    cx = layout.WINDOW_WIDTH // 2
    surface.blit(title, (cx - title.get_width() // 2, 20))


_GOLD_RIGHT_MARGIN = 20


def _draw_gold(
    surface: pygame.Surface, fonts: FontManager, gold: int,
) -> None:
    """Exibe gold no canto superior direito."""
    label = fonts.medium.render(f"Gold: {gold}", True, colors.TEXT_YELLOW)
    x = layout.WINDOW_WIDTH - label.get_width() - _GOLD_RIGHT_MARGIN
    surface.blit(label, (x, 24))


def _draw_panel_header(
    surface: pygame.Surface,
    fonts: FontManager,
    x: int,
    label: str,
) -> None:
    text = fonts.medium.render(label, True, _COLOR_HEADER)
    surface.blit(text, (x, _PANEL_TOP))


def _draw_controls(
    surface: pygame.Surface, fonts: FontManager,
) -> None:
    y = layout.WINDOW_HEIGHT - 30
    cx = layout.WINDOW_WIDTH // 2
    hint = "[A/D] Panel  [W/S] Navigate  [ENTER] Equip/Unequip  [ESC] Exit"
    text = fonts.small.render(hint, True, _COLOR_NEUTRAL)
    surface.blit(text, (cx - text.get_width() // 2, y))
