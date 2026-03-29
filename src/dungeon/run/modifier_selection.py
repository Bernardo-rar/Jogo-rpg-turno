"""ModifierSelection — logica pura de selecao de modifiers pre-run."""

from __future__ import annotations

from random import Random

from src.dungeon.modifiers.run_modifier import RunModifier


class ModifierSelection:
    """Oferece N modifiers aleatorios e permite toggle de selecao."""

    def __init__(
        self,
        pool: list[RunModifier],
        rng: Random,
        count: int = 3,
    ) -> None:
        self._offered = rng.sample(pool, min(count, len(pool)))
        self._active: set[int] = set()

    @property
    def offered(self) -> list[RunModifier]:
        """Modifiers oferecidos nesta rodada."""
        return list(self._offered)

    def toggle(self, index: int) -> None:
        """Alterna selecao do modifier no indice dado."""
        if not (0 <= index < len(self._offered)):
            return
        if index in self._active:
            self._active.discard(index)
        else:
            self._active.add(index)

    @property
    def selected(self) -> list[RunModifier]:
        """Retorna modifiers ativamente selecionados, em ordem."""
        return [self._offered[i] for i in sorted(self._active)]
