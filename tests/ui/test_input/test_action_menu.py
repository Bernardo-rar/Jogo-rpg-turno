"""Testes para ActionMenu — menu hierarquico que produz PlayerAction."""

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.combat_engine import TurnContext
from src.core.combat.player_action import PlayerActionType
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
from src.ui.input.action_menu import ActionMenu
from src.ui.input.menu_state import MenuLevel

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
        slot_cost=3, cooldown_turns=3,
    )


def _heal_self() -> Skill:
    return Skill(
        skill_id="heal", name="Heal", mana_cost=5,
        action_type=ActionType.ACTION, target_type=TargetType.SELF,
        effects=(SkillEffect(effect_type=SkillEffectType.HEAL, base_power=15),),
        slot_cost=2,
    )


def _aoe_fire() -> Skill:
    return Skill(
        skill_id="aoe", name="Fire Storm", mana_cost=15,
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


def _base_attrs() -> Attributes:
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, 10)
    return attrs


def _char_with_skills(name: str, *skills: Skill) -> Character:
    bar = SkillBar(slots=(SpellSlot(max_cost=20, skills=skills),))
    config = CharacterConfig(
        class_modifiers=SIMPLE_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        skill_bar=bar,
    )
    return Character(name, _base_attrs(), config)


def _char_with_inventory(name: str, inventory: Inventory) -> Character:
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
        enemies = [_build_char("Goblin")]
    return TurnContext(
        combatant=combatant,
        allies=[combatant],
        enemies=enemies,
        action_economy=economy or ActionEconomy(),
        round_number=1,
    )


class TestMenuNavigation:
    def test_starts_at_action_type(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        assert menu.current_level == MenuLevel.ACTION_TYPE

    def test_select_action_advances_to_specific(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        result = menu.select(1)
        assert result is None
        assert menu.current_level == MenuLevel.SPECIFIC_ACTION

    def test_select_basic_attack_advances_to_targets(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        result = menu.select(1)  # Basic Attack
        assert result is None
        assert menu.current_level == MenuLevel.TARGET_SELECT

    def test_select_target_returns_player_action(self):
        hero = _build_char("Hero")
        enemy = _build_char("Goblin")
        menu = ActionMenu(_ctx(hero, enemies=[enemy]))
        menu.select(1)  # Action
        menu.select(1)  # Basic Attack
        result = menu.select(1)  # Goblin
        assert result is not None
        assert result.action_type == PlayerActionType.BASIC_ATTACK
        assert result.target_name == "Goblin"

    def test_cancel_goes_back_one_level(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action → level 2
        assert menu.cancel() is True
        assert menu.current_level == MenuLevel.ACTION_TYPE

    def test_cancel_at_top_returns_false(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        assert menu.cancel() is False


class TestImmediateActions:
    def test_end_turn_returns_immediately(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        keys = [o.key for o in menu.options]
        end_key = max(keys)
        result = menu.select(end_key)
        assert result is not None
        assert result.action_type == PlayerActionType.END_TURN

    def test_move_returns_immediately(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(2)  # Bonus Action
        result = menu.select(1)  # Move
        assert result is not None
        assert result.action_type == PlayerActionType.MOVE

    def test_defend_returns_immediately(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(3)  # Reaction
        result = menu.select(1)  # Defend
        assert result is not None
        assert result.action_type == PlayerActionType.DEFEND


class TestAutoTargetSkills:
    def test_self_skill_skips_target_select(self):
        hero = _char_with_skills("Hero", _heal_self())
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        result = menu.select(2)  # Heal (SELF)
        assert result is not None
        assert result.action_type == PlayerActionType.SKILL
        assert result.skill_id == "heal"

    def test_all_enemies_skips_target_select(self):
        hero = _char_with_skills("Hero", _aoe_fire())
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        result = menu.select(2)  # Fire Storm (ALL_ENEMIES)
        assert result is not None
        assert result.action_type == PlayerActionType.SKILL
        assert result.skill_id == "aoe"


class TestOptionBuilding:
    def test_no_action_hides_option(self):
        hero = _build_char("Hero")
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        menu = ActionMenu(_ctx(hero, economy=economy))
        keys = [o.key for o in menu.options]
        assert 1 not in keys

    def test_skills_show_mana_cost(self):
        hero = _char_with_skills("Hero", _fireball())
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        skill_opt = next(o for o in menu.options if o.key == 2)
        assert "10" in skill_opt.label

    def test_skills_on_cooldown_unavailable(self):
        hero = _char_with_skills("Hero", _fireball())
        hero.skill_bar.cooldown_tracker.start_cooldown("fireball", 3)
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        skill_opt = next(o for o in menu.options if o.key == 2)
        assert skill_opt.available is False
        assert skill_opt.reason != ""

    def test_item_shows_quantity(self):
        inv = Inventory()
        inv.add_item(_health_potion(), quantity=3)
        hero = _char_with_inventory("Hero", inv)
        menu = ActionMenu(_ctx(hero))
        menu.select(4)  # Item
        item_opt = menu.options[0]
        assert "3" in item_opt.label

    def test_unavailable_option_ignored(self):
        hero = _char_with_skills("Hero", _fireball())
        hero.skill_bar.cooldown_tracker.start_cooldown("fireball", 3)
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        result = menu.select(2)  # Fireball (on cooldown)
        assert result is None
        assert menu.current_level == MenuLevel.SPECIFIC_ACTION

    def test_invalid_key_ignored(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        result = menu.select(9)
        assert result is None
        assert menu.current_level == MenuLevel.ACTION_TYPE
