"""Skill Pool Builder — monta pool de skills disponiveis por classe/level."""

from __future__ import annotations

from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_class_skills, load_skills


def build_skill_pool(
    class_id: str, level: int, subclass_id: str = "",
) -> list[Skill]:
    """Monta pool de skills filtrado por level.

    Combina: universal + class + subclass (se informado).
    Filtra por required_level <= level.
    """
    pool: dict[str, Skill] = {}
    pool.update(_load_universal(level))
    pool.update(_load_class(class_id, level))
    if subclass_id:
        pool.update(_load_subclass(subclass_id, level))
    return list(pool.values())


def _load_universal(level: int) -> dict[str, Skill]:
    """Carrega skills universais filtradas por level."""
    return _filter_by_level(load_skills(), level)


def _load_class(class_id: str, level: int) -> dict[str, Skill]:
    """Carrega skills de classe filtradas por level."""
    return _filter_by_level(load_class_skills(class_id), level)


def _load_subclass(subclass_id: str, level: int) -> dict[str, Skill]:
    """Carrega skills de subclasse filtradas por level."""
    try:
        skills = load_class_skills(f"subclass_{subclass_id}")
    except FileNotFoundError:
        return {}
    return _filter_by_level(skills, level)


def _filter_by_level(
    skills: dict[str, Skill], level: int,
) -> dict[str, Skill]:
    """Filtra skills por required_level."""
    return {
        sid: sk for sid, sk in skills.items()
        if sk.required_level <= level
    }
