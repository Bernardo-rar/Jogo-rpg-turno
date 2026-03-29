"""Event actions — aplica efeitos de escolhas de eventos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.dungeon.events.event_template import EventChoice, EventEffect

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.dungeon.run.run_state import RunState


def apply_event_choice(
    run_state: RunState,
    choice: EventChoice,
) -> dict[str, object]:
    """Aplica todos os efeitos de uma escolha no run_state."""
    summary: dict[str, object] = {
        "gold_delta": 0, "hp_delta": 0, "mana_delta": 0,
    }
    for effect in choice.effects:
        _apply_single_effect(run_state, effect, summary)
    return summary


def _apply_single_effect(
    run_state: RunState,
    effect: EventEffect,
    summary: dict[str, object],
) -> None:
    """Aplica um unico efeito e atualiza o resumo."""
    handlers = {
        "GOLD": _apply_gold,
        "HP_PERCENT": _apply_hp_percent,
        "MANA_PERCENT": _apply_mana_percent,
    }
    handler = handlers.get(effect.effect_type)
    if handler is not None:
        handler(run_state, effect.value, summary)


def _apply_gold(
    run_state: RunState,
    value: float,
    summary: dict[str, object],
) -> None:
    """Adiciona ou remove gold, sem ir abaixo de zero."""
    delta = int(value)
    run_state.gold = max(0, run_state.gold + delta)
    summary["gold_delta"] = int(summary["gold_delta"]) + delta


def _apply_hp_percent(
    run_state: RunState,
    value: float,
    summary: dict[str, object],
) -> None:
    """Aplica heal/damage percentual no HP da party."""
    total_delta = 0
    for c in run_state.party:
        if not c.is_alive:
            continue
        total_delta += _apply_hp_to_char(c, value)
    summary["hp_delta"] = int(summary["hp_delta"]) + total_delta


def _apply_hp_to_char(char: Character, pct: float) -> int:
    """Aplica percentual de HP a um personagem."""
    amount = int(abs(pct) * char.max_hp)
    if pct > 0:
        return char.heal(amount)
    char.take_damage(amount)
    return -amount


def _apply_mana_percent(
    run_state: RunState,
    value: float,
    summary: dict[str, object],
) -> None:
    """Aplica restore/drain percentual de mana na party."""
    total_delta = 0
    for c in run_state.party:
        if not c.is_alive:
            continue
        total_delta += _apply_mana_to_char(c, value)
    summary["mana_delta"] = int(summary["mana_delta"]) + total_delta


def _apply_mana_to_char(char: Character, pct: float) -> int:
    """Aplica percentual de mana a um personagem."""
    amount = int(abs(pct) * char.max_mana)
    if pct > 0:
        return char.restore_mana(amount)
    char.spend_mana(min(amount, char.current_mana))
    return -amount
