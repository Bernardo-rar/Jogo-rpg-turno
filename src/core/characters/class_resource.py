"""Protocols para recursos de classe (AP, Fury, Holy Power, etc)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class GainableResource(Protocol):
    """Recurso que pode ser ganho e lido."""

    @property
    def current(self) -> int: ...

    def gain(self, amount: int = 1) -> int: ...


@runtime_checkable
class SpendableResource(GainableResource, Protocol):
    """Recurso que pode ser ganho, lido e gasto."""

    def spend(self, amount: int) -> bool: ...
