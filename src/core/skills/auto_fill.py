"""Auto-fill de spell loadout — preenche slots automaticamente."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.skills.loadout_manager import LoadoutManager
from src.core.skills.skill import Skill


def auto_fill_loadout(
    pool: list[Skill], manager: LoadoutManager,
) -> None:
    """Preenche loadout greedily com skills de maior custo.

    Prioriza: reactions primeiro, passives, depois main slots.
    """
    manager.clear_all()
    _fill_reaction(pool, manager)
    _fill_passives(pool, manager)
    _fill_main_slots(pool, manager)


def _fill_reaction(pool: list[Skill], manager: LoadoutManager) -> None:
    """Coloca a primeira reaction skill encontrada."""
    for skill in _sorted_by_cost(pool):
        if skill.action_type == ActionType.REACTION:
            if manager.set_reaction(skill):
                return


def _fill_passives(pool: list[Skill], manager: LoadoutManager) -> None:
    """Preenche passivas ate o limite."""
    for skill in _sorted_by_cost(pool):
        if skill.action_type == ActionType.PASSIVE:
            manager.add_passive(skill)


def _fill_main_slots(pool: list[Skill], manager: LoadoutManager) -> None:
    """Preenche main slots greedily (maior cost primeiro)."""
    main_skills = [
        s for s in _sorted_by_cost(pool)
        if s.action_type in (ActionType.ACTION, ActionType.BONUS_ACTION)
    ]
    for skill in main_skills:
        _try_add_to_any_slot(skill, manager)


def _try_add_to_any_slot(skill: Skill, manager: LoadoutManager) -> None:
    """Tenta adicionar skill ao primeiro slot com budget."""
    for i in range(len(manager.slots)):
        if manager.add_skill(i, skill):
            return


def _sorted_by_cost(pool: list[Skill]) -> list[Skill]:
    """Ordena skills por slot_cost decrescente."""
    return sorted(pool, key=lambda s: s.slot_cost, reverse=True)
