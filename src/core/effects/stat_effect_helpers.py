"""Helpers compartilhados para StatBuff, StatDebuff e DebuffAilment."""

from __future__ import annotations

from src.core.effects.effect import PERMANENT_DURATION
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier

MINIMUM_DURATION = 1


def format_stat_name(stat: ModifiableStat) -> str:
    """PHYSICAL_ATTACK -> 'Physical Attack', MAX_HP -> 'Max HP'."""
    special = {"HP": "HP", "MANA": "Mana"}
    words = stat.name.split("_")
    result: list[str] = []
    for word in words:
        upper = special.get(word)
        result.append(upper if upper else word.capitalize())
    return " ".join(result)


def validate_duration(duration: int) -> None:
    """Valida que duracao e >= 1 ou PERMANENT_DURATION."""
    if duration != PERMANENT_DURATION and duration < MINIMUM_DURATION:
        raise ValueError(
            f"Invalid duration {duration}: must be >= {MINIMUM_DURATION}"
            f" or PERMANENT_DURATION ({PERMANENT_DURATION})",
        )


def validate_buff_modifier(modifier: StatModifier) -> None:
    """Valida que modifier tem valores nao-negativos."""
    if modifier.flat < 0 or modifier.percent < 0.0:
        raise ValueError(
            "Buff modifier values must be non-negative"
            f" (got flat={modifier.flat}, percent={modifier.percent})",
        )
    if modifier.flat == 0 and modifier.percent == 0.0:
        raise ValueError(
            "Buff must have at least one non-zero modifier",
        )


def validate_debuff_modifier(modifier: StatModifier) -> None:
    """Valida que modifier tem valores nao-positivos."""
    if modifier.flat > 0 or modifier.percent > 0.0:
        raise ValueError(
            "Debuff modifier values must be non-positive"
            f" (got flat={modifier.flat}, percent={modifier.percent})",
        )
    if modifier.flat == 0 and modifier.percent == 0.0:
        raise ValueError(
            "Debuff must have at least one non-zero modifier",
        )
