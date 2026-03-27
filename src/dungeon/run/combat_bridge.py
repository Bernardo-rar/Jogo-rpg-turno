"""Combat Bridge — prepara e finaliza combates dentro de uma run."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import TYPE_CHECKING

from src.dungeon.economy.gold_reward import (
    CombatInfo,
    GoldReward,
    calculate_combat_gold,
)
from src.dungeon.loot.loot_resolver import (
    LootResult,
    resolve_combat_loot,
)

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.dungeon.loot.drop_table import LootDrop
    from src.dungeon.run.run_state import RunState


@dataclass(frozen=True)
class CombatRewardContext:
    """Contexto para calcular recompensas pos-combate."""

    info: CombatInfo
    rng: Random


@dataclass(frozen=True)
class CombatRewardResult:
    """Resultado das recompensas de um combate."""

    gold_earned: int
    drops: tuple[LootDrop, ...]


def prepare_for_combat(party: list[Character]) -> None:
    """Limpa effects residuais antes do combate."""
    for c in party:
        if c.is_alive:
            c.effect_manager.clear_all()


def after_combat(
    run_state: RunState,
    node_id: str,
    reward_ctx: CombatRewardContext | None = None,
) -> CombatRewardResult | None:
    """Marca no visitado, atualiza progresso e resolve recompensas."""
    _mark_node_visited(run_state, node_id)
    if reward_ctx is None:
        return None
    return _resolve_rewards(run_state, reward_ctx)


def _mark_node_visited(
    run_state: RunState, node_id: str,
) -> None:
    """Marca no como visitado e incrementa progresso."""
    node = run_state.floor_map.get_node(node_id)
    if node is not None:
        node.visited = True
    run_state.current_node_id = node_id
    run_state.rooms_cleared += 1


def _resolve_rewards(
    run_state: RunState, ctx: CombatRewardContext,
) -> CombatRewardResult:
    """Calcula gold com multiplicador e resolve loot."""
    gold_earned = _grant_gold_with_mult(run_state, ctx)
    drops = _resolve_and_store_loot(run_state, ctx)
    return CombatRewardResult(
        gold_earned=gold_earned, drops=drops,
    )


def _grant_gold_with_mult(
    run_state: RunState, ctx: CombatRewardContext,
) -> int:
    """Calcula gold, aplica gold_mult, e adiciona ao state."""
    reward = calculate_combat_gold(ctx.info, ctx.rng)
    gold_mult = run_state.aggregated_effects.gold_mult
    earned = int(reward.total * gold_mult)
    run_state.gold += earned
    return earned


def _resolve_and_store_loot(
    run_state: RunState, ctx: CombatRewardContext,
) -> tuple[LootDrop, ...]:
    """Resolve drops e adiciona ao pending_loot."""
    loot = resolve_combat_loot(ctx.info, ctx.rng)
    run_state.pending_loot.extend(loot.drops)
    return loot.drops


def grant_combat_gold(
    run_state: RunState, info: CombatInfo, rng: Random,
) -> GoldReward:
    """Calcula e adiciona gold ao run_state."""
    reward = calculate_combat_gold(info, rng)
    run_state.gold += reward.total
    return reward
