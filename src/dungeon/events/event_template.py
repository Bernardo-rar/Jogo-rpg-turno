"""Event template — dataclasses para eventos aleatorios."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EventEffect:
    """Um efeito aplicado por uma escolha de evento."""

    effect_type: str
    value: float


@dataclass(frozen=True)
class EventChoice:
    """Uma opcao de escolha em um evento."""

    label: str
    effects: tuple[EventEffect, ...]
    result_text: str


@dataclass(frozen=True)
class EventTemplate:
    """Template de um evento aleatorio."""

    event_id: str
    title: str
    description: str
    choices: tuple[EventChoice, ...]
