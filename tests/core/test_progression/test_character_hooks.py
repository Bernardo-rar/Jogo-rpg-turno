"""Testes para hooks de level up no Character e subclasses."""

from unittest.mock import patch

import pytest

from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from tests.core.test_progression.conftest import (
    EMPTY_THRESHOLDS,
    SIMPLE_MODS,
    make_attrs,
)


class TestSetLevel:
    """Testes do _set_level no Character."""

    def test_set_level_changes_level(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=SIMPLE_MODS, threshold_calculator=calc)
        char = Character(name="Test", attributes=make_attrs(), config=config)
        assert char.level == 1
        char._set_level(5)
        assert char.level == 5

    def test_set_level_updates_max_hp(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=SIMPLE_MODS, threshold_calculator=calc)
        char = Character(name="Test", attributes=make_attrs(), config=config)
        hp_at_1 = char.max_hp
        char._set_level(3)
        assert char.max_hp > hp_at_1

    def test_set_level_updates_regen(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=SIMPLE_MODS, threshold_calculator=calc)
        char = Character(name="Test", attributes=make_attrs(), config=config)
        regen_at_1 = char.hp_regen
        char._set_level(3)
        assert char.hp_regen > regen_at_1

    def test_set_level_updates_proficiency_bonus(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=SIMPLE_MODS, threshold_calculator=calc)
        char = Character(name="Test", attributes=make_attrs(), config=config)
        assert char.proficiency_bonus == 1
        char._set_level(7)
        assert char.proficiency_bonus == 7

    def test_set_level_calls_on_level_up(self) -> None:
        """Verifica que on_level_up e chamado via _set_level."""
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=SIMPLE_MODS, threshold_calculator=calc)
        char = Character(name="Test", attributes=make_attrs(), config=config)
        with patch.object(char, "on_level_up") as mock_hook:
            char._set_level(2)
            mock_hook.assert_called_once()


class TestOnLevelUp:
    """Testes do hook on_level_up base."""

    def test_base_on_level_up_is_noop(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=SIMPLE_MODS, threshold_calculator=calc)
        char = Character(name="Test", attributes=make_attrs(), config=config)
        char.on_level_up()  # nao deve fazer nada nem levantar erro


class TestFighterLevelUpHook:
    """Testes do Fighter.on_level_up atualizando AP limit."""

    def test_fighter_ap_limit_updates_on_level_up(self) -> None:
        from src.core.classes.fighter.fighter import Fighter

        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(
            class_modifiers=SIMPLE_MODS,
            threshold_calculator=calc,
        )
        fighter = Fighter(name="Test", attributes=make_attrs(), config=config)
        assert fighter.action_points.limit == 2  # level 1
        fighter._set_level(3)
        assert fighter.action_points.limit == 6  # level 3

    def test_fighter_ap_limit_caps_at_default(self) -> None:
        from src.core.classes.fighter.fighter import Fighter

        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(
            class_modifiers=SIMPLE_MODS,
            threshold_calculator=calc,
        )
        fighter = Fighter(name="Test", attributes=make_attrs(), config=config)
        fighter._set_level(10)
        assert fighter.action_points.limit == 10  # DEFAULT_AP_LIMIT


class TestActionPointsUpdateLimit:
    """Testes do ActionPoints.update_limit."""

    def test_update_limit_changes_limit(self) -> None:
        from src.core.classes.fighter.action_points import ActionPoints

        ap = ActionPoints(level=1)
        assert ap.limit == 2
        ap.update_limit(3)
        assert ap.limit == 6

    def test_update_limit_preserves_current(self) -> None:
        from src.core.classes.fighter.action_points import ActionPoints

        ap = ActionPoints(level=1)
        ap.gain(2)
        ap.update_limit(5)
        assert ap.current == 2
        assert ap.limit == 10
