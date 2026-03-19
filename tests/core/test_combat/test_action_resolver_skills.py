"""Testes para ActionResolver — skills e itens."""

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.action_resolver import resolve_player_action
from src.core.combat.combat_engine import EventType, TurnContext
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.core.items.consumable import Consumable
from src.core.items.consumable_category import ConsumableCategory
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType
from src.core.items.inventory import Inventory
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType

from tests.core.test_combat.conftest import (
    SIMPLE_MODS,
    EMPTY_THRESHOLDS,
    _build_char,
)


def _fireball() -> Skill:
    return Skill(
        skill_id="fireball", name="Fireball", mana_cost=10,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        effects=(SkillEffect(effect_type=SkillEffectType.DAMAGE, base_power=20),),
        slot_cost=3,
    )


def _heal_skill() -> Skill:
    return Skill(
        skill_id="heal", name="Heal", mana_cost=5,
        action_type=ActionType.ACTION, target_type=TargetType.SELF,
        effects=(SkillEffect(effect_type=SkillEffectType.HEAL, base_power=15),),
        slot_cost=2, cooldown_turns=2,
    )


def _aoe_fire() -> Skill:
    return Skill(
        skill_id="aoe_fire", name="Fire Storm", mana_cost=15,
        action_type=ActionType.ACTION, target_type=TargetType.ALL_ENEMIES,
        effects=(SkillEffect(effect_type=SkillEffectType.DAMAGE, base_power=10),),
        slot_cost=3,
    )


def _health_potion() -> Consumable:
    return Consumable(
        consumable_id="health_potion", name="Health Potion",
        category=ConsumableCategory.HEALING, mana_cost=0,
        target_type=TargetType.SELF,
        effects=(ConsumableEffect(
            effect_type=ConsumableEffectType.HEAL_HP, base_power=30,
        ),),
    )


def _make_bar(*skills: Skill) -> SkillBar:
    slot = SpellSlot(max_cost=20, skills=skills)
    return SkillBar(slots=(slot,))


def _base_attrs() -> Attributes:
    """Cria Attributes com todos os valores em 10."""
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, 10)
    return attrs


def _char_with_skills(name: str, *skills: Skill) -> Character:
    """Cria Character com skill_bar contendo as skills dadas."""
    config = CharacterConfig(
        class_modifiers=SIMPLE_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        skill_bar=_make_bar(*skills),
    )
    return Character(name, _base_attrs(), config)


def _char_with_inventory(name: str, inventory: Inventory) -> Character:
    """Cria Character com inventario."""
    config = CharacterConfig(
        class_modifiers=SIMPLE_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        inventory=inventory,
    )
    return Character(name, _base_attrs(), config)


def _ctx(
    combatant: Character,
    enemies: list[Character] | None = None,
    economy: ActionEconomy | None = None,
) -> TurnContext:
    if enemies is None:
        enemies = [_build_char("Enemy")]
    return TurnContext(
        combatant=combatant,
        allies=[combatant],
        enemies=enemies,
        action_economy=economy or ActionEconomy(),
        round_number=1,
    )


class TestResolveSkill:
    def test_deals_damage_to_target(self):
        hero = _char_with_skills("Hero", _fireball())
        enemy = _build_char("Goblin")
        ctx = _ctx(hero, enemies=[enemy])
        hp_before = enemy.current_hp
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="fireball",
            target_name="Goblin",
        )
        events = resolve_player_action(action, ctx)
        assert len(events) == 1
        assert enemy.current_hp < hp_before

    def test_consumes_mana(self):
        hero = _char_with_skills("Hero", _fireball())
        ctx = _ctx(hero)
        mana_before = hero.current_mana
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="fireball",
            target_name="Enemy",
        )
        resolve_player_action(action, ctx)
        assert hero.current_mana == mana_before - 10

    def test_starts_cooldown(self):
        hero = _char_with_skills("Hero", _heal_skill())
        hero.take_damage(20)
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="heal",
        )
        resolve_player_action(action, ctx)
        tracker = hero.skill_bar.cooldown_tracker
        assert not tracker.is_ready("heal")
        assert tracker.remaining("heal") == 2

    def test_consumes_action_type(self):
        hero = _char_with_skills("Hero", _fireball())
        economy = ActionEconomy()
        ctx = _ctx(hero, economy=economy)
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="fireball",
            target_name="Enemy",
        )
        resolve_player_action(action, ctx)
        assert not economy.is_available(ActionType.ACTION)

    def test_insufficient_mana_returns_empty(self):
        hero = _char_with_skills("Hero", _fireball())
        hero.drain_mana(hero.current_mana)
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="fireball",
            target_name="Enemy",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_on_cooldown_returns_empty(self):
        hero = _char_with_skills("Hero", _fireball())
        hero.skill_bar.cooldown_tracker.start_cooldown("fireball", 3)
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="fireball",
            target_name="Enemy",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_self_target_heals_caster(self):
        hero = _char_with_skills("Hero", _heal_skill())
        hero.take_damage(20)
        hp_after_damage = hero.current_hp
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="heal",
        )
        events = resolve_player_action(action, ctx)
        assert len(events) == 1
        assert events[0].event_type == EventType.HEAL
        assert hero.current_hp > hp_after_damage

    def test_all_enemies_hits_everyone(self):
        hero = _char_with_skills("Hero", _aoe_fire())
        e1 = _build_char("Goblin_A")
        e2 = _build_char("Goblin_B")
        ctx = _ctx(hero, enemies=[e1, e2])
        hp1 = e1.current_hp
        hp2 = e2.current_hp
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="aoe_fire",
        )
        events = resolve_player_action(action, ctx)
        assert len(events) == 2
        assert e1.current_hp < hp1
        assert e2.current_hp < hp2

    def test_no_skill_bar_returns_empty(self):
        hero = _build_char("Hero")
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="fireball",
            target_name="Enemy",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_unknown_skill_id_returns_empty(self):
        hero = _char_with_skills("Hero", _fireball())
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="nonexistent",
            target_name="Enemy",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_no_action_available_returns_empty(self):
        hero = _char_with_skills("Hero", _fireball())
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        ctx = _ctx(hero, economy=economy)
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            skill_id="fireball",
            target_name="Enemy",
        )
        events = resolve_player_action(action, ctx)
        assert events == []


class TestResolveItem:
    def test_heals_target(self):
        inv = Inventory()
        inv.add_item(_health_potion(), quantity=3)
        hero = _char_with_inventory("Hero", inv)
        hero.take_damage(20)
        hp_after_damage = hero.current_hp
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        events = resolve_player_action(action, ctx)
        assert len(events) == 1
        assert events[0].event_type == EventType.HEAL
        assert hero.current_hp > hp_after_damage

    def test_removes_from_inventory(self):
        inv = Inventory()
        inv.add_item(_health_potion(), quantity=3)
        hero = _char_with_inventory("Hero", inv)
        hero.take_damage(20)
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        resolve_player_action(action, ctx)
        assert inv.get_quantity("health_potion") == 2

    def test_consumes_action(self):
        inv = Inventory()
        inv.add_item(_health_potion(), quantity=1)
        hero = _char_with_inventory("Hero", inv)
        hero.take_damage(20)
        economy = ActionEconomy()
        ctx = _ctx(hero, economy=economy)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        resolve_player_action(action, ctx)
        assert not economy.is_available(ActionType.ACTION)

    def test_no_inventory_returns_empty(self):
        hero = _build_char("Hero")
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_not_in_inventory_returns_empty(self):
        inv = Inventory()
        hero = _char_with_inventory("Hero", inv)
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_insufficient_mana_returns_empty(self):
        expensive_item = Consumable(
            consumable_id="mana_item", name="Mana Item",
            category=ConsumableCategory.HEALING, mana_cost=9999,
            target_type=TargetType.SELF,
            effects=(ConsumableEffect(
                effect_type=ConsumableEffectType.HEAL_HP, base_power=10,
            ),),
        )
        inv = Inventory()
        inv.add_item(expensive_item, quantity=1)
        hero = _char_with_inventory("Hero", inv)
        ctx = _ctx(hero)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="mana_item",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_no_action_available_returns_empty(self):
        inv = Inventory()
        inv.add_item(_health_potion(), quantity=1)
        hero = _char_with_inventory("Hero", inv)
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        ctx = _ctx(hero, economy=economy)
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            consumable_id="health_potion",
        )
        events = resolve_player_action(action, ctx)
        assert events == []
