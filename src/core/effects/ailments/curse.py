"""Curse - bloqueia habilidades baseadas em aura."""

from __future__ import annotations

from src.core.effects.ailments.resource_lock_ailment import ResourceLockAilment


class Curse(ResourceLockAilment):
    """Maldicao: impede uso de habilidades de aura."""

    @property
    def blocks_mana_skills(self) -> bool:
        return False

    @property
    def blocks_aura_skills(self) -> bool:
        return True
