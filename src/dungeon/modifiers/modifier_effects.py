"""Agregação de efeitos de múltiplos RunModifiers."""

from __future__ import annotations

from src.dungeon.modifiers.run_modifier import ModifierEffect, RunModifier

# Campos que se multiplicam entre si
_MULTIPLICATIVE_FIELDS = (
    "damage_taken_mult",
    "damage_dealt_mult",
    "healing_mult",
    "gold_mult",
    "elite_spawn_mult",
    "boss_stat_mult",
    "score_mult",
)


def aggregate_modifiers(
    modifiers: list[RunModifier],
) -> ModifierEffect:
    """Agrega efeitos de múltiplos modifiers em um único ModifierEffect.

    Campos multiplicativos são multiplicados entre si.
    start_hp_pct usa o mínimo (mais restritivo).
    """
    if not modifiers:
        return ModifierEffect()
    multiplied = _multiply_fields(modifiers)
    min_hp = _min_start_hp(modifiers)
    return ModifierEffect(**multiplied, start_hp_pct=min_hp)


def _multiply_fields(
    modifiers: list[RunModifier],
) -> dict[str, float]:
    """Multiplica campos multiplicativos de todos os modifiers."""
    result: dict[str, float] = {f: 1.0 for f in _MULTIPLICATIVE_FIELDS}
    for mod in modifiers:
        for field_name in _MULTIPLICATIVE_FIELDS:
            result[field_name] *= getattr(mod.effect, field_name)
    return result


def _min_start_hp(modifiers: list[RunModifier]) -> float:
    """Retorna o menor start_hp_pct (mais restritivo)."""
    return min(mod.effect.start_hp_pct for mod in modifiers)
