"""Arquétipos de comportamento de inimigos."""

from __future__ import annotations

from enum import Enum


class EnemyArchetype(Enum):
    """Define o padrão de IA do monstro."""

    DPS = "dps"
    TANK = "tank"
    HEALER = "healer"
    CONTROLLER = "controller"
