"""CcAilment ABC - base para Crowd Control ailments."""

from __future__ import annotations

from src.core.effects.ailments.status_ailment import StatusAilment


class CcAilment(StatusAilment):
    """Base para CC ailments (Freeze, Paralysis).

    CC ailments podem impedir o personagem de agir no turno.
    Subclasses implementam _do_tick() retornando skip_turn conforme logica.
    """

    @property
    def is_crowd_control(self) -> bool:
        """Sempre True para CC ailments."""
        return True
