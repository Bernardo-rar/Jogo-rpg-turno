"""Testes para o sistema de drop tables."""

from __future__ import annotations

from random import Random

from src.dungeon.loot.drop_table import (
    DropEntry,
    DropTable,
    LootDrop,
    resolve_drops,
)


class TestLootDrop:

    def test_frozen_dataclass(self) -> None:
        drop = LootDrop(
            item_type="consumable", item_id="health_potion",
        )
        assert drop.item_type == "consumable"
        assert drop.item_id == "health_potion"
        assert drop.quantity == 1


class TestDropTable:

    def test_drop_table_holds_entries(self) -> None:
        entry = DropEntry(
            item_type="consumable",
            item_id="health_potion",
            weight=40,
        )
        table = DropTable(drops=(entry,))
        assert len(table.drops) == 1


class TestResolveDrops:

    def _make_table(self) -> DropTable:
        entries = (
            DropEntry(
                item_type="consumable",
                item_id="health_potion",
                weight=40,
            ),
            DropEntry(
                item_type="consumable",
                item_id="mana_potion",
                weight=30,
            ),
            DropEntry(
                item_type="consumable",
                item_id="antidote",
                weight=20,
            ),
            DropEntry(
                item_type="consumable",
                item_id="molotov",
                weight=10,
            ),
        )
        return DropTable(drops=entries)

    def test_resolve_drops_returns_correct_count(self) -> None:
        table = self._make_table()
        rng = Random(42)
        drops = resolve_drops(table, count=3, rng=rng)
        assert len(drops) == 3

    def test_resolve_drops_items_from_pool(self) -> None:
        table = self._make_table()
        rng = Random(42)
        drops = resolve_drops(table, count=5, rng=rng)
        valid_ids = {e.item_id for e in table.drops}
        for drop in drops:
            assert drop.item_id in valid_ids

    def test_weighted_selection_favors_high_weight(self) -> None:
        table = self._make_table()
        rng = Random(42)
        sample_size = 1000
        drops = resolve_drops(table, count=sample_size, rng=rng)
        health_count = sum(
            1 for d in drops if d.item_id == "health_potion"
        )
        molotov_count = sum(
            1 for d in drops if d.item_id == "molotov"
        )
        assert health_count > molotov_count

    def test_resolve_drops_returns_loot_drop_type(self) -> None:
        table = self._make_table()
        rng = Random(42)
        drops = resolve_drops(table, count=1, rng=rng)
        assert isinstance(drops[0], LootDrop)

    def test_resolve_drops_zero_count(self) -> None:
        table = self._make_table()
        rng = Random(42)
        drops = resolve_drops(table, count=0, rng=rng)
        assert drops == []
