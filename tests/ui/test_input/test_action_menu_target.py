"""Testes para highlighted_target e select_highlighted no ActionMenu."""

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.combat.action_economy import ActionEconomy
from src.core.combat.combat_engine import TurnContext
from src.core.combat.player_action import PlayerActionType
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType
from src.core.combat.action_economy import ActionType
from src.ui.input.action_menu import ActionMenu
from src.ui.input.menu_state import MenuLevel

from tests.core.test_combat.conftest import (
    SIMPLE_MODS,
    EMPTY_THRESHOLDS,
    _build_char,
)


def _base_attrs() -> Attributes:
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, 10)
    return attrs


def _heal_ally() -> Skill:
    return Skill(
        skill_id="heal_ally", name="Heal Ally", mana_cost=5,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ALLY,
        effects=(SkillEffect(effect_type=SkillEffectType.HEAL, base_power=15),),
        slot_cost=2,
    )


def _char_with_skills(name: str, *skills: Skill) -> Character:
    bar = SkillBar(slots=(SpellSlot(max_cost=20, skills=skills),))
    config = CharacterConfig(
        class_modifiers=SIMPLE_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        skill_bar=bar,
    )
    return Character(name, _base_attrs(), config)


def _ctx(
    combatant: Character,
    enemies: list[Character] | None = None,
    allies: list[Character] | None = None,
) -> TurnContext:
    if enemies is None:
        enemies = [_build_char("Goblin")]
    if allies is None:
        allies = [combatant]
    return TurnContext(
        combatant=combatant,
        allies=allies,
        enemies=enemies,
        action_economy=ActionEconomy(),
        round_number=1,
    )


def _go_to_target_select(menu: ActionMenu) -> None:
    """Navega ate nivel TARGET_SELECT via Basic Attack."""
    menu.select(1)  # Action
    menu.select(1)  # Basic Attack


class TestHighlightedTarget:
    def test_highlighted_target_none_at_action_type(self) -> None:
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        assert menu.highlighted_target is None

    def test_highlighted_target_none_at_specific_action(self) -> None:
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero))
        menu.select(1)  # Action → level 2
        assert menu.highlighted_target is None

    def test_highlighted_target_returns_first_enemy_at_target_select(self) -> None:
        hero = _build_char("Hero")
        goblin = _build_char("Goblin")
        orc = _build_char("Orc")
        menu = ActionMenu(_ctx(hero, enemies=[goblin, orc]))
        _go_to_target_select(menu)
        assert menu.highlighted_target == "Goblin"

    def test_highlighted_target_cycles_with_move_highlight(self) -> None:
        hero = _build_char("Hero")
        goblin = _build_char("Goblin")
        orc = _build_char("Orc")
        menu = ActionMenu(_ctx(hero, enemies=[goblin, orc]))
        _go_to_target_select(menu)
        menu.move_highlight(1)
        assert menu.highlighted_target == "Orc"

    def test_highlighted_target_wraps_around(self) -> None:
        hero = _build_char("Hero")
        goblin = _build_char("Goblin")
        orc = _build_char("Orc")
        menu = ActionMenu(_ctx(hero, enemies=[goblin, orc]))
        _go_to_target_select(menu)
        menu.move_highlight(1)  # Orc
        menu.move_highlight(1)  # wraps to Goblin
        assert menu.highlighted_target == "Goblin"


class TestSelectHighlighted:
    def test_select_highlighted_returns_player_action(self) -> None:
        hero = _build_char("Hero")
        goblin = _build_char("Goblin")
        orc = _build_char("Orc")
        menu = ActionMenu(_ctx(hero, enemies=[goblin, orc]))
        _go_to_target_select(menu)
        menu.move_highlight(1)  # highlight Orc
        result = menu.select_highlighted()
        assert result is not None
        assert result.action_type == PlayerActionType.BASIC_ATTACK
        assert result.target_name == "Orc"

    def test_select_highlighted_empty_returns_none(self) -> None:
        hero = _build_char("Hero")
        menu = ActionMenu(_ctx(hero, enemies=[]))
        # No enemies, so Action → level 2 only has Basic Attack
        menu.select(1)  # Action
        menu.select(1)  # Basic Attack — no targets → stays at level 2
        # No targets available, highlighted_target should be None
        result = menu.select_highlighted()
        assert result is None
