"""Testes para consumiveis custarem BONUS_ACTION em vez de ACTION."""

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.action_resolver import resolve_player_action
from src.core.combat.combat_engine import TurnContext
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.core.items.consumable import Consumable
from src.core.items.consumable_category import ConsumableCategory
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType
from src.core.items.inventory import Inventory
from src.core.skills.target_type import TargetType

from tests.core.test_combat.conftest import _build_char


def _health_potion() -> Consumable:
    return Consumable(
        consumable_id="health_potion", name="Health Potion",
        category=ConsumableCategory.HEALING, mana_cost=0,
        target_type=TargetType.SELF,
        effects=(ConsumableEffect(
            effect_type=ConsumableEffectType.HEAL_HP, base_power=30,
        ),),
    )


def _ctx_with_item(economy: ActionEconomy | None = None) -> TurnContext:
    """Cria contexto com heroi que tem potion e sofreu dano."""
    hero = _build_char("Hero")
    hero.take_damage(10)
    hero._inventory = Inventory()
    hero._inventory.add_item(_health_potion())
    eco = economy or ActionEconomy()
    return TurnContext(
        combatant=hero, allies=[hero],
        enemies=[_build_char("Goblin")],
        action_economy=eco, round_number=1,
    )


class TestItemCostsBonusAction:
    def test_item_consumes_bonus_action(self) -> None:
        economy = ActionEconomy()
        ctx = _ctx_with_item(economy)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        events = resolve_player_action(action, ctx)
        assert len(events) == 1
        assert not economy.is_available(ActionType.BONUS_ACTION)

    def test_item_does_not_consume_action(self) -> None:
        economy = ActionEconomy()
        ctx = _ctx_with_item(economy)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        resolve_player_action(action, ctx)
        assert economy.is_available(ActionType.ACTION)

    def test_can_attack_and_use_item_same_turn(self) -> None:
        economy = ActionEconomy()
        ctx = _ctx_with_item(economy)
        attack = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin",
        )
        resolve_player_action(attack, ctx)
        assert not economy.is_available(ActionType.ACTION)
        assert economy.is_available(ActionType.BONUS_ACTION)
        item = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        events = resolve_player_action(item, ctx)
        assert len(events) == 1
        assert not economy.is_available(ActionType.BONUS_ACTION)

    def test_no_bonus_action_blocks_item(self) -> None:
        economy = ActionEconomy()
        economy.use(ActionType.BONUS_ACTION)
        ctx = _ctx_with_item(economy)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        events = resolve_player_action(action, ctx)
        assert events == []
