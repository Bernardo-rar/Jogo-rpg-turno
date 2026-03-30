"""CombatRewardHandler — logica de recompensas e XP pos-combate."""

from __future__ import annotations

from random import Random
from typing import TYPE_CHECKING

from src.dungeon.economy.gold_reward import CombatInfo
from src.dungeon.run.combat_bridge import (
    CombatRewardContext,
    CombatRewardResult,
    after_combat,
    mark_node_visited,
)
from src.dungeon.run.loot_distributor import distribute_consumables
from src.core.progression.xp_calculator import CombatXpInput, calculate_combat_xp

if TYPE_CHECKING:
    from src.core.items.consumable import Consumable
    from src.core.progression.level_up_system import LevelUpSystem
    from src.core.progression.xp_reward_config import XpRewardConfig
    from src.dungeon.run.run_state import RunState


class CombatRewardHandler:
    """Encapsula logica de recompensas e XP pos-combate."""

    def __init__(
        self,
        xp_config: XpRewardConfig,
    ) -> None:
        self._xp_config = xp_config
        self.last_reward: CombatRewardResult | None = None

    def handle_post_combat(
        self,
        result: dict,
        state: RunState,
        combat_ctx: CombatContext,
        level_system: LevelUpSystem | None,
        consumable_catalog: dict[str, Consumable],
    ) -> None:
        """Processa resultado do combate: gold, loot, XP."""
        result["is_boss"] = combat_ctx.is_boss
        result["party_alive"] = state.is_party_alive
        if not combat_ctx.node_id:
            return
        ctx = _build_reward_context(state, combat_ctx)
        reward = after_combat(state, combat_ctx.node_id, ctx)
        xp_result = _grant_combat_xp(
            result, state, combat_ctx, level_system, self._xp_config,
        )
        if reward is not None and xp_result is not None:
            reward = _merge_xp_into_reward(reward, xp_result)
        self.last_reward = reward
        _collect_consumables(state, consumable_catalog)

    def handle_post_room(
        self,
        state: RunState,
        node_id: str | None,
        consumable_catalog: dict[str, Consumable],
    ) -> None:
        """Marca no como visitado apos sala nao-combate."""
        if node_id is None:
            return
        mark_node_visited(state, node_id)
        _collect_consumables(state, consumable_catalog)


class CombatContext:
    """Dados contextuais do combate atual."""

    def __init__(self) -> None:
        self.node_id: str | None = None
        self.is_boss: bool = False
        self.is_elite: bool = False
        self.enemy_count: int = 0

    def reset(self) -> None:
        self.node_id = None
        self.is_boss = False
        self.is_elite = False
        self.enemy_count = 0


def _build_reward_context(
    state: RunState,
    combat_ctx: CombatContext,
) -> CombatRewardContext:
    """Cria contexto de recompensa para o combate atual."""
    info = CombatInfo(
        enemy_count=combat_ctx.enemy_count,
        tier=1,
        is_elite=combat_ctx.is_elite,
        is_boss=combat_ctx.is_boss,
    )
    rng = Random(state.seed + hash(combat_ctx.node_id))
    return CombatRewardContext(info=info, rng=rng)


def _encounter_type(combat_ctx: CombatContext) -> str:
    """Retorna tipo de encontro para calculo de XP."""
    if combat_ctx.is_boss:
        return "boss"
    if combat_ctx.is_elite:
        return "elite"
    return "normal"


def _grant_combat_xp(
    result: dict,
    state: RunState,
    combat_ctx: CombatContext,
    level_system: LevelUpSystem | None,
    xp_config: object,
) -> tuple[int, bool, int] | None:
    """Calcula e aplica XP do combate."""
    if level_system is None:
        return None
    if not result.get("victory", False):
        return None
    enc_type = _encounter_type(combat_ctx)
    combat_input = CombatXpInput(
        encounter_type=enc_type,
        tier=1,
        rounds=result.get("rounds", 10),
        party_deaths=result.get("deaths", 0),
        xp_run_mult=state.aggregated_effects.xp_mult,
    )
    xp = calculate_combat_xp(combat_input, xp_config)
    level_result = level_system.gain_party_xp(state.party, xp)
    leveled = level_result is not None
    new_level = level_result.new_level if leveled else 0
    return (xp, leveled, new_level)


def _merge_xp_into_reward(
    reward: CombatRewardResult,
    xp_result: tuple[int, bool, int],
) -> CombatRewardResult:
    """Combina XP result no CombatRewardResult."""
    return CombatRewardResult(
        gold_earned=reward.gold_earned,
        drops=reward.drops,
        xp_earned=xp_result[0],
        leveled_up=xp_result[1],
        new_level=xp_result[2],
    )


def _collect_consumables(
    state: RunState,
    consumable_catalog: dict[str, object],
) -> None:
    """Move consumiveis do pending_loot pro inventario."""
    remaining = distribute_consumables(
        state.party,
        state.pending_loot,
        consumable_catalog,
    )
    state.pending_loot = remaining


def check_level_points(
    reward: CombatRewardResult | None,
) -> bool:
    """Verifica se o level up deu pontos pra distribuir."""
    if reward is None or not reward.leveled_up:
        return False
    from src.core.progression.attribute_point_config import (
        get_points_for_level,
        load_attribute_points,
    )
    config = load_attribute_points()
    pts = get_points_for_level(reward.new_level, config)
    return pts.total > 0
