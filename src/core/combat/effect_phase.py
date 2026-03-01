"""Fase de efeitos no combate - funcoes puras para tick/apply/skip."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.characters.character import Character
from src.core.effects.effect_manager import EffectManager
from src.core.effects.tick_result import TickResult


@dataclass(frozen=True)
class EffectLogEntry:
    """Registro de um efeito que ocorreu durante a fase de efeitos."""

    round_number: int
    character_name: str
    value: int = 0
    message: str = ""
    is_skip: bool = False


def process_effect_ticks(effect_manager: EffectManager) -> list[TickResult]:
    """Ticka todos os efeitos ativos. Retorna lista de resultados."""
    return effect_manager.tick_all()


def apply_tick_results(
    character: Character,
    results: list[TickResult],
    round_number: int,
) -> list[EffectLogEntry]:
    """Aplica dano/cura/mana dos ticks no personagem. Retorna log entries."""
    entries: list[EffectLogEntry] = []
    for result in results:
        if not character.is_alive:
            break
        entry = _apply_single_tick(character, result, round_number)
        if entry is not None:
            entries.append(entry)
    return entries


def should_skip_turn(results: list[TickResult]) -> bool:
    """True se algum efeito impede o personagem de agir."""
    return any(r.skip_turn for r in results)


def create_skip_entry(
    character_name: str, round_number: int, message: str,
) -> EffectLogEntry:
    """Cria entry para turno pulado por CC."""
    return EffectLogEntry(
        round_number=round_number,
        character_name=character_name,
        message=message,
        is_skip=True,
    )


def _apply_single_tick(
    character: Character,
    result: TickResult,
    round_number: int,
) -> EffectLogEntry | None:
    """Aplica um TickResult e retorna log entry se houve efeito."""
    if result.damage > 0:
        character.take_damage(result.damage)
        return _create_entry(character, result, round_number)
    if result.healing > 0:
        character.heal(result.healing)
        return _create_entry(character, result, round_number)
    if result.mana_change != 0:
        _apply_mana_change(character, result.mana_change)
        return _create_entry(character, result, round_number)
    return None


def _apply_mana_change(character: Character, mana_change: int) -> None:
    """Aplica mudanca de mana (positiva ou negativa)."""
    if mana_change > 0:
        character.restore_mana(mana_change)
    else:
        character.drain_mana(abs(mana_change))


def _create_entry(
    character: Character,
    result: TickResult,
    round_number: int,
) -> EffectLogEntry:
    """Cria EffectLogEntry para um tick de efeito."""
    if result.damage > 0:
        value = result.damage
    elif result.healing > 0:
        value = result.healing
    else:
        value = abs(result.mana_change)
    return EffectLogEntry(
        round_number=round_number,
        character_name=character.name,
        value=value,
        message=result.message,
    )
