"""SpellSlot frozen dataclass com budget de custo para skills."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.skills.skill import Skill


@dataclass(frozen=True)
class SpellSlot:
    """Slot de spell com budget maximo de custo."""

    max_cost: int
    skills: tuple[Skill, ...] = ()


def total_slot_cost(slot: SpellSlot) -> int:
    """Soma o slot_cost de todas as skills no slot."""
    return sum(s.slot_cost for s in slot.skills)


def fits_in_slot(slot: SpellSlot, skill: Skill) -> bool:
    """True se a skill cabe no budget restante do slot."""
    return total_slot_cost(slot) + skill.slot_cost <= slot.max_cost


def add_skill_to_slot(slot: SpellSlot, skill: Skill) -> SpellSlot | None:
    """Adiciona skill ao slot. Retorna novo SpellSlot ou None se nao cabe."""
    if not fits_in_slot(slot, skill):
        return None
    return SpellSlot(
        max_cost=slot.max_cost,
        skills=slot.skills + (skill,),
    )
