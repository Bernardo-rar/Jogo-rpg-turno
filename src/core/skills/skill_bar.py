"""SkillBar - barra de skills do personagem com slots e cooldowns."""

from __future__ import annotations

from src.core.skills.cooldown_tracker import CooldownTracker
from src.core.skills.skill import Skill
from src.core.skills.spell_slot import SpellSlot


class SkillBar:
    """Barra de skills: agrega SpellSlots e rastreia cooldowns."""

    def __init__(self, slots: tuple[SpellSlot, ...]) -> None:
        self._slots = slots
        self._cooldown_tracker = CooldownTracker()

    @property
    def slots(self) -> tuple[SpellSlot, ...]:
        return self._slots

    @property
    def cooldown_tracker(self) -> CooldownTracker:
        return self._cooldown_tracker

    @property
    def all_skills(self) -> list[Skill]:
        """Todas as skills equipadas em todos os slots."""
        return [sk for slot in self._slots for sk in slot.skills]

    @property
    def ready_skills(self) -> list[Skill]:
        """Skills equipadas que nao estao em cooldown."""
        return [
            sk for sk in self.all_skills
            if self._cooldown_tracker.is_ready(sk.skill_id)
        ]
