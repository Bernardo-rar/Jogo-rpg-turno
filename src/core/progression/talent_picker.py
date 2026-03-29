"""Talent picker — gera 3 opcoes de talento com diversidade de categoria."""

from __future__ import annotations

from random import Random

from src.core.progression.talent_config import Talent


def generate_talent_offering(
    class_id: str,
    all_talents: dict[str, Talent],
    chosen_ids: set[str],
    rng: Random,
) -> list[Talent]:
    """Gera 3 talentos para escolha com diversidade de categoria."""
    eligible = _filter_eligible(class_id, all_talents, chosen_ids)
    if len(eligible) <= 3:
        return eligible
    return _pick_diverse(eligible, rng)


def _filter_eligible(
    class_id: str,
    all_talents: dict[str, Talent],
    chosen_ids: set[str],
) -> list[Talent]:
    """Filtra talentos elegiveis para a classe."""
    return [
        t for t in all_talents.values()
        if t.talent_id not in chosen_ids
        and t.is_available_for(class_id)
    ]


def _pick_diverse(
    eligible: list[Talent], rng: Random,
) -> list[Talent]:
    """Pega 1 de cada categoria, preenche o resto."""
    by_cat = _group_by_category(eligible)
    picks: list[Talent] = []
    picked_ids: set[str] = set()
    for cat in ("OFFENSIVE", "DEFENSIVE", "UTILITY"):
        pool = by_cat.get(cat, [])
        _pick_from_pool(pool, picks, picked_ids, rng)
    _fill_remaining(eligible, picks, picked_ids, rng)
    return picks[:3]


def _group_by_category(
    talents: list[Talent],
) -> dict[str, list[Talent]]:
    groups: dict[str, list[Talent]] = {}
    for t in talents:
        groups.setdefault(t.category, []).append(t)
    return groups


def _pick_from_pool(
    pool: list[Talent],
    picks: list[Talent],
    picked_ids: set[str],
    rng: Random,
) -> None:
    """Pega 1 talento aleatório do pool se possível."""
    available = [t for t in pool if t.talent_id not in picked_ids]
    if available and len(picks) < 3:
        choice = rng.choice(available)
        picks.append(choice)
        picked_ids.add(choice.talent_id)


def _fill_remaining(
    eligible: list[Talent],
    picks: list[Talent],
    picked_ids: set[str],
    rng: Random,
) -> None:
    """Preenche ate 3 com talentos restantes."""
    remaining = [t for t in eligible if t.talent_id not in picked_ids]
    while len(picks) < 3 and remaining:
        choice = rng.choice(remaining)
        picks.append(choice)
        picked_ids.add(choice.talent_id)
        remaining.remove(choice)
