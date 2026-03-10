"""Posiciona e renderiza CharacterCards no campo de batalha."""

from __future__ import annotations

import pygame

from src.core.characters.position import Position
from src.ui import layout
from src.ui.components.character_card import draw_character_card
from src.ui.font_manager import FontManager
from src.ui.replay.battle_snapshot import CharacterSnapshot, RoundSnapshot


class Battlefield:
    """Arranja personagens no campo: inimigos a esquerda, party a direita."""

    def __init__(self, snapshot: RoundSnapshot) -> None:
        self._snapshot = snapshot

    def update(self, snapshot: RoundSnapshot) -> None:
        """Atualiza estado dos personagens."""
        self._snapshot = snapshot

    def draw(self, surface: pygame.Surface, fonts: FontManager) -> None:
        """Desenha todos os character cards."""
        enemies = [s for s in self._snapshot.characters if not s.is_party]
        party = [s for s in self._snapshot.characters if s.is_party]
        _draw_team(surface, enemies, is_party=False, fonts=fonts)
        _draw_team(surface, party, is_party=True, fonts=fonts)


def _draw_team(
    surface: pygame.Surface,
    team: list[CharacterSnapshot],
    *,
    is_party: bool,
    fonts: FontManager,
) -> None:
    start_y = layout.ENEMY_START_Y if not is_party else layout.PARTY_START_Y
    for i, snap in enumerate(team):
        x = _pick_x(snap.position, is_party)
        y = start_y + i * layout.CARD_SPACING_Y
        draw_character_card(surface, snap, x, y, fonts)


def _pick_x(position: Position, is_party: bool) -> int:
    if is_party:
        return layout.PARTY_FRONT_X if position == Position.FRONT else layout.PARTY_BACK_X
    return layout.ENEMY_FRONT_X if position == Position.FRONT else layout.ENEMY_BACK_X
