"""Amnesia - bloqueia habilidades baseadas em mana."""

from __future__ import annotations

from src.core.effects.ailments.resource_lock_ailment import ResourceLockAilment


class Amnesia(ResourceLockAilment):
    """Amnesia: impede uso de habilidades que custam mana."""

    @property
    def blocks_mana_skills(self) -> bool:
        return True

    @property
    def blocks_aura_skills(self) -> bool:
        return False
