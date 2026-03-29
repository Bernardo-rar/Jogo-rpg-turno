"""LoadoutManager — gerencia customizacao de spell loadout."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.spell_slot import SpellSlot, fits_in_slot, add_skill_to_slot


class LoadoutManager:
    """Gerencia slots de skills com validacao de budget."""

    def __init__(self, slot_count: int, budget: int) -> None:
        self._slots = [SpellSlot(max_cost=budget) for _ in range(slot_count)]
        self._reaction: Skill | None = None
        self._passives: list[Skill] = []
        self._passive_limit = 2
        self._assigned_ids: set[str] = set()

    @property
    def slots(self) -> list[SpellSlot]:
        return list(self._slots)

    @property
    def reaction(self) -> Skill | None:
        return self._reaction

    @property
    def passives(self) -> list[Skill]:
        return list(self._passives)

    def add_skill(self, slot_index: int, skill: Skill) -> bool:
        """Adiciona skill ao slot. Retorna False se nao cabe."""
        if skill.skill_id in self._assigned_ids:
            return False
        if slot_index >= len(self._slots):
            return False
        new_slot = add_skill_to_slot(self._slots[slot_index], skill)
        if new_slot is None:
            return False
        self._slots[slot_index] = new_slot
        self._assigned_ids.add(skill.skill_id)
        return True

    def remove_skill(self, slot_index: int, skill_id: str) -> bool:
        """Remove skill do slot pelo ID."""
        if slot_index >= len(self._slots):
            return False
        slot = self._slots[slot_index]
        remaining = tuple(s for s in slot.skills if s.skill_id != skill_id)
        if len(remaining) == len(slot.skills):
            return False
        self._slots[slot_index] = SpellSlot(
            max_cost=slot.max_cost, skills=remaining,
        )
        self._assigned_ids.discard(skill_id)
        return True

    def set_reaction(self, skill: Skill) -> bool:
        """Define skill de reacao. Retorna False se invalida."""
        if skill.action_type != ActionType.REACTION:
            return False
        if self._reaction is not None:
            self._assigned_ids.discard(self._reaction.skill_id)
        self._reaction = skill
        self._assigned_ids.add(skill.skill_id)
        return True

    def add_passive(self, skill: Skill) -> bool:
        """Adiciona passiva. Retorna False se limite atingido."""
        if skill.action_type != ActionType.PASSIVE:
            return False
        if len(self._passives) >= self._passive_limit:
            return False
        if skill.skill_id in self._assigned_ids:
            return False
        self._passives.append(skill)
        self._assigned_ids.add(skill.skill_id)
        return True

    def clear_all(self) -> None:
        """Limpa todos os slots, reacao e passivas."""
        budget = self._slots[0].max_cost if self._slots else 8
        self._slots = [
            SpellSlot(max_cost=budget) for _ in range(len(self._slots))
        ]
        self._reaction = None
        self._passives.clear()
        self._assigned_ids.clear()

    def build_skill_bar(self) -> SkillBar:
        """Constroi SkillBar a partir do loadout atual."""
        all_skills: list[Skill] = []
        for slot in self._slots:
            all_skills.extend(slot.skills)
        if self._reaction is not None:
            all_skills.append(self._reaction)
        all_skills.extend(self._passives)
        total_cost = sum(s.slot_cost for s in all_skills)
        budget = max(total_cost + 10, 100)
        master_slot = SpellSlot(max_cost=budget, skills=tuple(all_skills))
        return SkillBar(slots=(master_slot,))
