"""Testes para drops de equipamento (weapon, armor, accessory)."""

from __future__ import annotations

from random import Random

from src.dungeon.economy.gold_reward import CombatInfo
from src.dungeon.loot.drop_table import (
    DropEntry,
    DropTable,
    LootDrop,
    resolve_drops,
)
from src.dungeon.loot.loot_resolver import (
    DropTableConfig,
    load_drop_tables,
    resolve_combat_loot,
)
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.run.combat_bridge import (
    CombatRewardContext,
    after_combat,
)
from src.dungeon.run.run_state import RunState
from tests.core.test_combat.conftest import _build_char


class TestDropTableCanContainWeapons:

    def test_drop_table_can_contain_weapons(self) -> None:
        """Weapon item_type in drop pool works."""
        entries = (
            DropEntry(
                item_type="weapon",
                item_id="flame_sword",
                weight=100,
            ),
        )
        table = DropTable(drops=entries)
        rng = Random(42)
        drops = resolve_drops(table, count=1, rng=rng)
        assert len(drops) == 1
        assert drops[0].item_type == "weapon"
        assert drops[0].item_id == "flame_sword"


class TestDropTableCanContainArmor:

    def test_drop_table_can_contain_armor(self) -> None:
        """Armor item_type in drop pool works."""
        entries = (
            DropEntry(
                item_type="armor",
                item_id="studded_leather",
                weight=100,
            ),
        )
        table = DropTable(drops=entries)
        rng = Random(42)
        drops = resolve_drops(table, count=1, rng=rng)
        assert len(drops) == 1
        assert drops[0].item_type == "armor"
        assert drops[0].item_id == "studded_leather"


class TestEquipmentDropsGoToStash:

    def _make_state(self) -> RunState:
        fm = MapGenerator().generate(seed=1)
        return RunState(
            seed=1, party=[_build_char("A")], floor_map=fm,
        )

    def _first_node_id(self, state: RunState) -> str:
        return state.floor_map.layers[0][0].node_id

    def _weapon_only_tables(self) -> dict[str, DropTableConfig]:
        """Cria drop table com apenas weapon drops."""
        entries = (
            DropEntry(
                item_type="weapon",
                item_id="flame_sword",
                weight=100,
            ),
        )
        config = DropTableConfig(
            table=DropTable(drops=entries),
            min_drops=1,
            max_drops=1,
        )
        return {"tier1": config}

    def test_equipment_drops_go_to_stash(self) -> None:
        """Weapon drops should go to equipment_stash, not pending_loot."""
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=1, tier=1)
        tables = self._weapon_only_tables()
        ctx = CombatRewardContext(info=info, rng=Random(42))
        after_combat(state, node_id, ctx, tables=tables)
        assert len(state.equipment_stash) == 1
        assert state.equipment_stash[0].item_type == "weapon"
        assert len(state.pending_loot) == 0


class TestConsumableDropsGoToPendingLoot:

    def _make_state(self) -> RunState:
        fm = MapGenerator().generate(seed=1)
        return RunState(
            seed=1, party=[_build_char("A")], floor_map=fm,
        )

    def _first_node_id(self, state: RunState) -> str:
        return state.floor_map.layers[0][0].node_id

    def _consumable_only_tables(self) -> dict[str, DropTableConfig]:
        """Cria drop table com apenas consumable drops."""
        entries = (
            DropEntry(
                item_type="consumable",
                item_id="health_potion",
                weight=100,
            ),
        )
        config = DropTableConfig(
            table=DropTable(drops=entries),
            min_drops=1,
            max_drops=1,
        )
        return {"tier1": config}

    def test_consumable_drops_go_to_pending_loot(self) -> None:
        """Consumable drops should still go to pending_loot."""
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=1, tier=1)
        tables = self._consumable_only_tables()
        ctx = CombatRewardContext(info=info, rng=Random(42))
        after_combat(state, node_id, ctx, tables=tables)
        assert len(state.pending_loot) == 1
        assert state.pending_loot[0].item_type == "consumable"
        assert len(state.equipment_stash) == 0


class TestMixedDropsRoutedCorrectly:

    def _make_state(self) -> RunState:
        fm = MapGenerator().generate(seed=1)
        return RunState(
            seed=1, party=[_build_char("A")], floor_map=fm,
        )

    def _first_node_id(self, state: RunState) -> str:
        return state.floor_map.layers[0][0].node_id

    def _mixed_tables(self) -> dict[str, DropTableConfig]:
        """Cria drop table com consumable + weapon + armor."""
        entries = (
            DropEntry(
                item_type="consumable",
                item_id="health_potion",
                weight=34,
            ),
            DropEntry(
                item_type="weapon",
                item_id="flame_sword",
                weight=33,
            ),
            DropEntry(
                item_type="armor",
                item_id="studded_leather",
                weight=33,
            ),
        )
        config = DropTableConfig(
            table=DropTable(drops=entries),
            min_drops=10,
            max_drops=10,
        )
        return {"tier1": config}

    def test_mixed_drops_routed_correctly(self) -> None:
        """Mix of consumable + equipment routed to correct lists."""
        state = self._make_state()
        node_id = self._first_node_id(state)
        info = CombatInfo(enemy_count=1, tier=1)
        tables = self._mixed_tables()
        ctx = CombatRewardContext(info=info, rng=Random(42))
        after_combat(state, node_id, ctx, tables=tables)
        all_loot_types = {d.item_type for d in state.pending_loot}
        all_stash_types = {d.item_type for d in state.equipment_stash}
        # pending_loot should only have consumables
        assert all_loot_types <= {"consumable"}
        # equipment_stash should have weapon and/or armor
        assert all_stash_types <= {"weapon", "armor", "accessory"}
        # With 10 drops, we should have at least some in each
        total = len(state.pending_loot) + len(state.equipment_stash)
        assert total == 10


class TestEquipmentStashOnRunState:

    def test_equipment_stash_starts_empty(self) -> None:
        """RunState should have an empty equipment_stash by default."""
        fm = MapGenerator().generate(seed=1)
        state = RunState(seed=1, party=[], floor_map=fm)
        assert state.equipment_stash == []

    def test_equipment_stash_accepts_drops(self) -> None:
        """equipment_stash should accept LootDrop items."""
        fm = MapGenerator().generate(seed=1)
        state = RunState(seed=1, party=[], floor_map=fm)
        drop = LootDrop(
            item_type="weapon", item_id="flame_sword",
        )
        state.equipment_stash.append(drop)
        assert len(state.equipment_stash) == 1
        assert state.equipment_stash[0].item_id == "flame_sword"


class TestDropTablesJsonContainsEquipment:

    def test_tier1_has_equipment_entries(self) -> None:
        """tier1 drop table should contain weapon/armor/accessory."""
        tables = load_drop_tables()
        tier1_entries = tables["tier1"].table.drops
        item_types = {e.item_type for e in tier1_entries}
        assert "weapon" in item_types or "armor" in item_types

    def test_boss1_has_equipment_entries(self) -> None:
        """boss1 should have equipment (guaranteed rarer drops)."""
        tables = load_drop_tables()
        boss_entries = tables["boss1"].table.drops
        item_types = {e.item_type for e in boss_entries}
        has_equipment = item_types & {"weapon", "armor", "accessory"}
        assert len(has_equipment) > 0
