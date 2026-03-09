"""Testes para ConsumableHandler - executa consumiveis no combate."""

from __future__ import annotations

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.combat_engine import EventType, TurnContext
from src.core.combat.consumable_handler import ConsumableHandler
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


def _smoke_bomb() -> Consumable:
    return Consumable(
        consumable_id="smoke_bomb", name="Smoke Bomb",
        category=ConsumableCategory.ESCAPE, mana_cost=0,
        target_type=TargetType.SELF,
        effects=(ConsumableEffect(
            effect_type=ConsumableEffectType.FLEE,
        ),),
    )


def _context(combatant, enemies=None):
    if enemies is None:
        enemies = [_build_char("Enemy")]
    return TurnContext(
        combatant=combatant,
        allies=[combatant],
        enemies=enemies,
        action_economy=ActionEconomy(),
        round_number=1,
    )


class TestConsumableHandler:
    def test_no_inventory_returns_empty(self) -> None:
        hero = _build_char("Hero")
        handler = ConsumableHandler()
        events = handler.execute_turn(_context(hero))
        assert events == []

    def test_empty_inventory_returns_empty(self) -> None:
        hero = _build_char("Hero")
        hero._inventory = Inventory()
        handler = ConsumableHandler()
        events = handler.execute_turn(_context(hero))
        assert events == []

    def test_uses_action(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(5)
        hero._inventory = Inventory()
        hero._inventory.add_item(_health_potion())
        economy = ActionEconomy()
        ctx = TurnContext(
            combatant=hero, allies=[hero],
            enemies=[_build_char("E")],
            action_economy=economy, round_number=1,
        )
        ConsumableHandler().execute_turn(ctx)
        assert not economy.is_available(ActionType.ACTION)

    def test_removes_from_inventory(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(5)
        hero._inventory = Inventory()
        hero._inventory.add_item(_health_potion(), quantity=2)
        handler = ConsumableHandler()
        handler.execute_turn(_context(hero))
        assert hero.inventory.get_quantity("health_potion") == 1

    def test_heal_creates_event(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(5)
        hero._inventory = Inventory()
        hero._inventory.add_item(_health_potion())
        handler = ConsumableHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1
        assert events[0].event_type == EventType.HEAL

    def test_no_action_available_returns_empty(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(5)
        hero._inventory = Inventory()
        hero._inventory.add_item(_health_potion())
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        ctx = TurnContext(
            combatant=hero, allies=[hero],
            enemies=[_build_char("E")],
            action_economy=economy, round_number=1,
        )
        events = ConsumableHandler().execute_turn(ctx)
        assert events == []

    def test_no_mana_returns_empty(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(5)
        costly = Consumable(
            consumable_id="expensive", name="Expensive",
            category=ConsumableCategory.HEALING, mana_cost=9999,
            target_type=TargetType.SELF,
            effects=(ConsumableEffect(
                effect_type=ConsumableEffectType.HEAL_HP, base_power=30,
            ),),
        )
        hero._inventory = Inventory()
        hero._inventory.add_item(costly)
        handler = ConsumableHandler()
        events = handler.execute_turn(_context(hero))
        assert events == []

    def test_flee_creates_flee_event(self) -> None:
        hero = _build_char("Hero")
        hero._inventory = Inventory()
        hero._inventory.add_item(_smoke_bomb())
        handler = ConsumableHandler()
        events = handler.execute_turn(_context(hero))
        assert len(events) == 1
        assert events[0].event_type == EventType.FLEE
