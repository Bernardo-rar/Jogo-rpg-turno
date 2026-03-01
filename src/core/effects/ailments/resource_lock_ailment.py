"""ResourceLockAilment ABC - base para ailments que bloqueiam habilidades."""

from __future__ import annotations

from abc import abstractmethod

from src.core.effects.ailments.status_ailment import StatusAilment


class ResourceLockAilment(StatusAilment):
    """Base para ailments que bloqueiam categorias de habilidades.

    Amnesia bloqueia skills de mana, Curse bloqueia skills de aura.
    Nao modificam stats nem causam dano - apenas flags.
    """

    @property
    @abstractmethod
    def blocks_mana_skills(self) -> bool:
        """True se impede uso de habilidades baseadas em mana."""
        ...

    @property
    @abstractmethod
    def blocks_aura_skills(self) -> bool:
        """True se impede uso de habilidades baseadas em aura."""
        ...
