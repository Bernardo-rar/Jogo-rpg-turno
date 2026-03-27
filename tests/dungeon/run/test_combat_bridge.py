"""Testes para combat_bridge."""

from random import Random

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_buff import StatBuff
from src.core.effects.stat_modifier import StatModifier
from src.dungeon.economy.gold_reward import CombatInfo
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.modifiers.run_modifier import (
    ModifierCategory,
    ModifierEffect,
    RunModifier,
)
from src.dungeon.run.combat_bridge import (
    CombatRewardContext,
    CombatRewardResult,
    after_combat,
    grant_combat_gold,
    prepare_for_combat,
)
from src.dungeon.run.run_state import RunState
from tests.core.test_combat.conftest import _build_char


class TestPrepareForCombat:

    def test_clears_effects_on_alive(self) -> None:
        char = _build_char("A")
        mod = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=5)
        buff = StatBuff(modifier=mod, duration=3)
        char.effect_manager.add_effect(buff)
        assert len(char.effect_manager.active_effects) > 0
        prepare_for_combat([char])
        assert len(char.effect_manager.active_effects) == 0

    def test_skips_dead_characters(self) -> None:
        char = _build_char("A")
        char.take_damage(char.max_hp)
        assert not char.is_alive
        # Nao deve dar erro em mortos
        prepare_for_combat([char])


class TestAfterCombat:

    def test_marks_node_visited(self) -> None:
        fm = MapGenerator().generate(seed=1)
        state = RunState(seed=1, party=[], floor_map=fm)
        node_id = fm.layers[0][0].node_id
        after_combat(state, node_id)
        assert fm.get_node(node_id).visited is True

    def test_updates_current_node(self) -> None:
        fm = MapGenerator().generate(seed=1)
        state = RunState(seed=1, party=[], floor_map=fm)
        node_id = fm.layers[0][0].node_id
        after_combat(state, node_id)
        assert state.current_node_id == node_id

    def test_increments_rooms_cleared(self) -> None:
        fm = MapGenerator().generate(seed=1)
        state = RunState(seed=1, party=[], floor_map=fm)
        node_id = fm.layers[0][0].node_id
        after_combat(state, node_id)
        assert state.rooms_cleared == 1


class TestGrantCombatGold:

    def _make_state(self) -> RunState:
        fm = MapGenerator().generate(seed=1)
        return RunState(seed=1, party=[], floor_map=fm)

    def test_adds_gold_to_run_state(self) -> None:
        state = self._make_state()
        rng = Random(42)
        info = CombatInfo(enemy_count=2, tier=1)
        reward = grant_combat_gold(state, info, rng)
        assert state.gold > 0
        assert state.gold == reward.total

    def test_accumulates_gold_across_combats(self) -> None:
        state = self._make_state()
        rng = Random(42)
        info = CombatInfo(enemy_count=2, tier=1)
        grant_combat_gold(state, info, rng)
        first_gold = state.gold
        grant_combat_gold(state, info, rng)
        assert state.gold > first_gold

    def test_returns_gold_reward(self) -> None:
        state = self._make_state()
        rng = Random(42)
        info = CombatInfo(enemy_count=1, tier=1)
        reward = grant_combat_gold(state, info, rng)
        assert reward.total == reward.base + reward.bonus


class TestAfterCombatRewards:
    """Testes para after_combat com CombatRewardContext."""

    def _make_state(self) -> RunState:
        fm = MapGenerator().generate(seed=1)
        return RunState(seed=1, party=[], floor_map=fm)

    def _first_node_id(self, state: RunState) -> str:
        return state.floor_map.layers[0][0].node_id

    def test_grants_gold_to_run_state(self) -> None:
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=3, tier=1)
        ctx = CombatRewardContext(info=info, rng=Random(99))
        after_combat(state, node_id, ctx)
        assert state.gold > 0

    def test_returns_combat_reward_result(self) -> None:
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=2, tier=1)
        ctx = CombatRewardContext(info=info, rng=Random(42))
        result = after_combat(state, node_id, ctx)
        assert isinstance(result, CombatRewardResult)
        assert result.gold_earned > 0

    def test_resolves_loot_drops_to_pending(self) -> None:
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=2, tier=1)
        ctx = CombatRewardContext(info=info, rng=Random(42))
        after_combat(state, node_id, ctx)
        assert len(state.pending_loot) > 0

    def test_gold_mult_applied(self) -> None:
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=3, tier=1)
        gold_mod = RunModifier(
            modifier_id="double_gold",
            name="Double Gold",
            description="2x gold",
            category=ModifierCategory.ECONOMY,
            effect=ModifierEffect(gold_mult=2.0),
        )
        state.active_modifiers.append(gold_mod)
        rng_seed = 77
        ctx = CombatRewardContext(info=info, rng=Random(rng_seed))
        after_combat(state, node_id, ctx)
        gold_with_mult = state.gold
        # Comparar com gold sem multiplicador
        state2 = self._make_state()
        node_id2 = state2.floor_map.layers[0][0].node_id
        ctx2 = CombatRewardContext(info=info, rng=Random(rng_seed))
        after_combat(state2, node_id2, ctx2)
        gold_without_mult = state2.gold
        assert gold_with_mult == gold_without_mult * 2

    def test_boss_fight_gives_boss_gold(self) -> None:
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=1, tier=1, is_boss=True)
        ctx = CombatRewardContext(info=info, rng=Random(42))
        result = after_combat(state, node_id, ctx)
        assert result.gold_earned > 0
        assert state.gold == result.gold_earned

    def test_no_context_returns_none(self) -> None:
        state = self._make_state()
        node_id = self._first_node_id(state)
        result = after_combat(state, node_id)
        assert result is None
        assert state.gold == 0

    def test_still_marks_visited_with_context(self) -> None:
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=1, tier=1)
        ctx = CombatRewardContext(info=info, rng=Random(1))
        after_combat(state, node_id, ctx)
        assert state.floor_map.get_node(node_id).visited is True
        assert state.rooms_cleared == 1
