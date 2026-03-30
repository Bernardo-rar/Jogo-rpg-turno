"""Testes para CombatRewardScene — tela de recompensas pos-combate."""

from __future__ import annotations

from src.dungeon.loot.drop_table import LootDrop
from src.ui.scenes.combat_reward_scene import (
    CombatRewardScene,
    RewardSceneConfig,
    humanize_item_id,
)


class TestHumanizeItemId:

    def test_snake_case_to_title(self) -> None:
        assert humanize_item_id("health_potion") == "Health Potion"

    def test_single_word(self) -> None:
        assert humanize_item_id("sword") == "Sword"

    def test_multiple_underscores(self) -> None:
        assert humanize_item_id("great_fire_axe") == "Great Fire Axe"


class TestCombatRewardScene:

    def test_gold_counter_reaches_target(self) -> None:
        completed: list[dict] = []
        scene = CombatRewardScene(
            fonts=None,
            config=RewardSceneConfig(
                gold_earned=100, drops=(), total_gold=500,
                on_complete=completed.append,
            ),
        )
        # Atualiza 2 segundos (mais que suficiente para a animacao)
        for _ in range(120):
            scene.update(dt_ms=17)
        assert scene.gold_displayed == 100

    def test_empty_drops_no_error(self) -> None:
        completed: list[dict] = []
        scene = CombatRewardScene(
            fonts=None,
            config=RewardSceneConfig(
                gold_earned=50, drops=(), total_gold=50,
                on_complete=completed.append,
            ),
        )
        # Deve funcionar sem drops
        scene.update(dt_ms=1000)
        assert scene.gold_displayed <= 50

    def test_counting_done_after_enough_time(self) -> None:
        completed: list[dict] = []
        scene = CombatRewardScene(
            fonts=None,
            config=RewardSceneConfig(
                gold_earned=200,
                drops=(LootDrop(item_type="consumable", item_id="health_potion", quantity=2),),
                total_gold=300,
                on_complete=completed.append,
            ),
        )
        # Atualiza bastante para completar contagem
        for _ in range(120):
            scene.update(dt_ms=17)
        assert scene.counting_done is True

    def test_zero_gold_immediately_done(self) -> None:
        completed: list[dict] = []
        scene = CombatRewardScene(
            fonts=None,
            config=RewardSceneConfig(
                gold_earned=0, drops=(), total_gold=0,
                on_complete=completed.append,
            ),
        )
        scene.update(dt_ms=17)
        assert scene.counting_done is True
        assert scene.gold_displayed == 0
