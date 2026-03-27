"""Testes para breadcrumb do ActionMenu."""

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.combat_engine import TurnContext
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType
from src.ui.input.action_menu import ActionMenu
from src.ui.input.menu_state import MenuLevel

from tests.core.test_combat.conftest import _build_char
from tests.ui.test_input.test_action_menu import (
    _base_attrs,
    _char_with_skills,
    _ctx,
    _fireball,
)


def _bonus_skill() -> Skill:
    return Skill(
        skill_id="quick_heal", name="Quick Heal", mana_cost=5,
        action_type=ActionType.BONUS_ACTION, target_type=TargetType.SINGLE_ENEMY,
        effects=(SkillEffect(effect_type=SkillEffectType.HEAL, base_power=10),),
        slot_cost=1,
    )


class TestBreadcrumb:
    def test_breadcrumb_empty_at_action_type(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        assert menu.breadcrumb == ""

    def test_breadcrumb_shows_category_at_specific_action(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        assert menu.current_level == MenuLevel.SPECIFIC_ACTION
        assert menu.breadcrumb == "Action"

    def test_breadcrumb_shows_category_and_skill_at_target_select(self):
        hero = _char_with_skills("Hero", _fireball())
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        menu.select(2)  # Fireball -> target select
        assert menu.current_level == MenuLevel.TARGET_SELECT
        assert menu.breadcrumb == "Action > Fireball"

    def test_breadcrumb_bonus_category(self):
        hero = _char_with_skills("Hero", _bonus_skill())
        menu = ActionMenu(_ctx(hero))
        menu.select(2)  # Bonus Action
        assert menu.current_level == MenuLevel.SPECIFIC_ACTION
        assert menu.breadcrumb == "Bonus Action"

    def test_cancel_from_specific_goes_back_and_clears_breadcrumb(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        assert menu.breadcrumb == "Action"
        menu.cancel()
        assert menu.current_level == MenuLevel.ACTION_TYPE
        assert menu.breadcrumb == ""

    def test_breadcrumb_basic_attack_at_target_select(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action
        menu.select(1)  # Basic Attack -> target select
        assert menu.current_level == MenuLevel.TARGET_SELECT
        assert menu.breadcrumb == "Action > Basic Attack"

    def test_breadcrumb_reaction_category(self):
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(3)  # Reaction
        assert menu.current_level == MenuLevel.SPECIFIC_ACTION
        assert menu.breadcrumb == "Reaction"

    def test_breadcrumb_item_category(self):
        from tests.ui.test_input.test_action_menu import (
            _char_with_inventory,
            _health_potion,
        )
        from src.core.items.inventory import Inventory
        inv = Inventory()
        inv.add_item(_health_potion(), quantity=1)
        hero = _char_with_inventory("Hero", inv)
        menu = ActionMenu(_ctx(hero))
        menu.select(4)  # Item
        assert menu.current_level == MenuLevel.SPECIFIC_ACTION
        assert menu.breadcrumb == "Item"
