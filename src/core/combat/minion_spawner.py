"""MinionSpawner — handles mid-combat minion summoning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.combat.combat_engine import CombatEvent, TurnHandler


@dataclass
class SpawnContext:
    """Context needed to spawn minions mid-combat."""

    enemies: list[Character]
    handler: TurnHandler
    add_combatant_fn: Callable
    round_number: int


def process_pending_summons(
    handler: TurnHandler,
    spawn_fn: Callable,
) -> None:
    """Checks handler for pending summon requests and spawns minions."""
    drain = getattr(handler, "drain_pending_summons", None)
    if drain is None:
        return
    for summon_cfg in drain():
        spawn_fn(summon_cfg)


def spawn_minion(
    summon_cfg: object, ctx: SpawnContext,
) -> CombatEvent | None:
    """Creates a minion Character from SummonConfig and adds it."""
    boss = _find_alive_boss(ctx.enemies)
    if boss is None:
        return None
    minion = _create_minion_char(summon_cfg, boss, ctx.handler)
    ctx.add_combatant_fn(minion, is_enemy=True)
    _register_minion(ctx.handler, minion.name)
    return _summon_event(ctx.round_number, boss.name, minion.name)


def _find_alive_boss(enemies: list[Character]) -> Character | None:
    alive = [c for c in enemies if c.is_alive]
    return alive[0] if alive else None


def _create_minion_char(
    cfg: object, boss: Character, handler: TurnHandler,
) -> Character:
    """Builds a minion Character from boss stats + config scales."""
    from src.core.attributes.attributes import Attributes
    from src.core.characters.character import Character
    from src.core.characters.character_config import CharacterConfig

    hp = max(1, int(boss.max_hp * cfg.hp_scale))
    atk = max(1, int(boss.attack_power * cfg.atk_scale))
    idx = len(_minion_names_from_handler(handler))
    name = f"{cfg.minion_template_id}_{idx}"
    mods = _build_minion_modifiers(hp, atk)
    return Character(name, Attributes(), CharacterConfig(class_modifiers=mods))


def _summon_event(
    round_number: int, boss_name: str, minion_name: str,
) -> CombatEvent:
    from src.core.combat.combat_engine import CombatEvent, EventType
    return CombatEvent(
        round_number=round_number,
        actor_name=boss_name,
        target_name=minion_name,
        event_type=EventType.SUMMON,
        description=f"{minion_name} appears!",
    )


def _build_minion_modifiers(hp: int, atk: int) -> object:
    """Creates ClassModifiers for a minion."""
    from src.core.characters.class_modifiers import ClassModifiers

    return ClassModifiers(
        hit_dice=hp // 4, mod_hp_flat=0, mod_hp_mult=1,
        mana_multiplier=0, mod_atk_physical=atk // 4,
        mod_atk_magical=0, mod_def_physical=2, mod_def_magical=2,
        regen_hp_mod=0, regen_mana_mod=0,
    )


def _minion_names_from_handler(handler: TurnHandler) -> list[str]:
    """Extracts existing minion names from handler."""
    names = getattr(handler, "_minion_names", [])
    return list(names)


def _register_minion(handler: TurnHandler, name: str) -> None:
    """Registers a minion name in the handler if supported."""
    reg = getattr(handler, "register_minion", None)
    if reg is not None:
        reg(name)
