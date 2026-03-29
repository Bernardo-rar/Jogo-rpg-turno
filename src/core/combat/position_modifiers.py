"""Position modifiers — multiplicadores de dano por posicao."""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.core._paths import resolve_data_path
from src.core.characters.position import Position

_CONFIG_FILE = "data/combat/position_modifiers.json"

_config: _PositionConfig | None = None


@dataclass(frozen=True)
class PositionMod:
    """Multiplicadores de uma posicao."""

    damage_dealt_mult: float
    damage_taken_mult: float


@dataclass(frozen=True)
class _PositionConfig:
    """Config de ambas posicoes."""

    front: PositionMod
    back: PositionMod


def get_position_mod(position: Position) -> PositionMod:
    """Retorna multiplicadores pra posicao dada."""
    cfg = _load_config()
    if position == Position.FRONT:
        return cfg.front
    return cfg.back


def scale_dealt(base: int, position: Position) -> int:
    """Escala dano causado pela posicao do atacante."""
    return max(1, int(base * get_position_mod(position).damage_dealt_mult))


def scale_taken(base: int, position: Position) -> int:
    """Escala dano recebido pela posicao do alvo."""
    return max(1, int(base * get_position_mod(position).damage_taken_mult))


def _load_config() -> _PositionConfig:
    global _config
    if _config is not None:
        return _config
    path = resolve_data_path(_CONFIG_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    _config = _PositionConfig(
        front=_parse_mod(raw["FRONT"]),
        back=_parse_mod(raw["BACK"]),
    )
    return _config


def _parse_mod(data: dict) -> PositionMod:
    return PositionMod(
        damage_dealt_mult=data["damage_dealt_mult"],
        damage_taken_mult=data["damage_taken_mult"],
    )
