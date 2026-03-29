"""CombatIntroAnimation — cards slide in from edges."""

from __future__ import annotations

SLIDE_DURATION_MS = 300
STAGGER_MS = 50
INITIAL_OFFSET = 400
TOTAL_DURATION_MS = 600


class CombatIntroAnimation:
    """Slides party cards from right, enemy cards from left."""

    def __init__(
        self,
        party_names: list[str],
        enemy_names: list[str],
    ) -> None:
        self.blocking = True
        self._elapsed = 0
        self._offsets: dict[str, int] = {}
        for i, name in enumerate(enemy_names):
            self._offsets[name] = -(INITIAL_OFFSET + i * STAGGER_MS)
        for i, name in enumerate(party_names):
            self._offsets[name] = INITIAL_OFFSET + i * STAGGER_MS

    def update(self, dt_ms: int) -> None:
        self._elapsed += dt_ms

    def draw(self, surface) -> None:
        pass

    @property
    def is_done(self) -> bool:
        return self._elapsed >= TOTAL_DURATION_MS

    def get_offsets(self) -> dict[str, tuple[int, int]]:
        """Returns (dx, dy) offset per character name."""
        result: dict[str, tuple[int, int]] = {}
        for name, base in self._offsets.items():
            direction = -1 if base < 0 else 1
            abs_base = abs(base)
            delay = abs_base - INITIAL_OFFSET if abs_base > INITIAL_OFFSET else 0
            effective = max(0, self._elapsed - abs(delay))
            t = min(1.0, effective / SLIDE_DURATION_MS)
            eased = 1.0 - (1.0 - t) ** 2
            offset = int(INITIAL_OFFSET * direction * (1.0 - eased))
            result[name] = (offset, 0)
        return result
