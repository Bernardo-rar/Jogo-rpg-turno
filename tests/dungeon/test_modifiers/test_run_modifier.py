"""Testes para RunModifier, ModifierEffect e modifier_loader."""

from src.dungeon.modifiers.run_modifier import (
    ModifierCategory,
    ModifierEffect,
    RunModifier,
)
from src.dungeon.modifiers.modifier_loader import load_modifiers

EXPECTED_MODIFIER_COUNT = 10


class TestModifierFromDict:

    def test_modifier_from_dict_creates_correct_instance(self) -> None:
        # Arrange
        data = {
            "name": "Frail",
            "description": "+15% damage taken, +15% gold",
            "category": "DIFFICULTY",
            "effect": {
                "damage_taken_mult": 1.15,
                "gold_mult": 1.15,
                "score_mult": 1.1,
            },
        }

        # Act
        modifier = RunModifier.from_dict("frail", data)

        # Assert
        assert modifier.modifier_id == "frail"
        assert modifier.name == "Frail"
        assert modifier.description == "+15% damage taken, +15% gold"

    def test_modifier_category_parsed(self) -> None:
        # Arrange
        data = {
            "name": "Poverty",
            "description": "-30% gold gain",
            "category": "ECONOMY",
            "effect": {"gold_mult": 0.7},
        }

        # Act
        modifier = RunModifier.from_dict("poverty", data)

        # Assert
        assert modifier.category is ModifierCategory.ECONOMY

    def test_modifier_effect_fields_populated(self) -> None:
        # Arrange
        data = {
            "name": "Frail",
            "description": "test",
            "category": "DIFFICULTY",
            "effect": {
                "damage_taken_mult": 1.15,
                "gold_mult": 1.15,
                "score_mult": 1.1,
            },
        }

        # Act
        modifier = RunModifier.from_dict("frail", data)

        # Assert
        assert modifier.effect.damage_taken_mult == 1.15
        assert modifier.effect.gold_mult == 1.15
        assert modifier.effect.score_mult == 1.1


class TestDefaultEffect:

    def test_default_effect_is_neutral(self) -> None:
        # Arrange / Act
        effect = ModifierEffect()

        # Assert
        assert effect.damage_taken_mult == 1.0
        assert effect.damage_dealt_mult == 1.0
        assert effect.healing_mult == 1.0
        assert effect.gold_mult == 1.0
        assert effect.elite_spawn_mult == 1.0
        assert effect.boss_stat_mult == 1.0
        assert effect.score_mult == 1.0
        assert effect.start_hp_pct == 1.0


class TestLoadModifiers:

    def test_load_modifiers_returns_all(self) -> None:
        # Act
        modifiers = load_modifiers()

        # Assert
        assert len(modifiers) == EXPECTED_MODIFIER_COUNT

    def test_load_modifiers_keys_match_ids(self) -> None:
        # Act
        modifiers = load_modifiers()

        # Assert
        for modifier_id, modifier in modifiers.items():
            assert modifier.modifier_id == modifier_id

    def test_load_modifiers_frail_exists(self) -> None:
        # Act
        modifiers = load_modifiers()

        # Assert
        assert "frail" in modifiers
        assert modifiers["frail"].category is ModifierCategory.DIFFICULTY
