"""CooldownTracker - rastreia cooldowns de skills por combate."""

from __future__ import annotations

NO_COOLDOWN = 0


class CooldownTracker:
    """Rastreia cooldown restante de skills. Tick por turno, reset por combate."""

    def __init__(self) -> None:
        self._cooldowns: dict[str, int] = {}

    def start_cooldown(self, skill_id: str, turns: int) -> None:
        """Inicia cooldown para uma skill. Sobrescreve se ja existir."""
        if turns > NO_COOLDOWN:
            self._cooldowns[skill_id] = turns

    def tick(self) -> None:
        """Decrementa todos os cooldowns em 1. Remove os que chegaram a 0."""
        expired = []
        for skill_id in self._cooldowns:
            self._cooldowns[skill_id] -= 1
            if self._cooldowns[skill_id] <= NO_COOLDOWN:
                expired.append(skill_id)
        for skill_id in expired:
            del self._cooldowns[skill_id]

    def is_ready(self, skill_id: str) -> bool:
        """True se a skill nao esta em cooldown."""
        return skill_id not in self._cooldowns

    def remaining(self, skill_id: str) -> int:
        """Turnos restantes de cooldown. 0 se pronta."""
        return self._cooldowns.get(skill_id, NO_COOLDOWN)

    def reset(self) -> None:
        """Limpa todos os cooldowns (inicio de combate)."""
        self._cooldowns.clear()
