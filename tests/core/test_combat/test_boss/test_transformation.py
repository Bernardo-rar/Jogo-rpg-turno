"""Tests for boss transformation logic."""

from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.combat.boss.boss_transformation import (
    TransformationConfig,
    apply_transformation,
)

from tests.core.test_combat.conftest import _build_char as _make_char


def _make_transform_config() -> TransformationConfig:
    new_mods = ClassModifiers(
        hit_dice=20,
        mod_hp_flat=10,
        mod_hp_mult=7,
        mana_multiplier=0,
        mod_atk_physical=10,
        mod_atk_magical=6,
        mod_def_physical=8,
        mod_def_magical=8,
        regen_hp_mod=3,
        regen_mana_mod=0,
    )
    return TransformationConfig(
        hp_threshold=0.30,
        new_name="Awakened Golem",
        battle_cry="The Golem's ancient seal breaks!",
        heal_pct=0.20,
        new_class_modifiers=new_mods,
        new_elemental_profile_id="fire_strong",
        new_position=Position.FRONT,
    )


class TestTransformationConfig:

    def test_from_dict(self) -> None:
        data = {
            "hp_threshold": 0.30,
            "new_name": "X",
            "battle_cry": "Roar!",
            "heal_pct": 0.2,
            "new_class_modifiers": {
                "hit_dice": 10,
                "mod_hp_flat": 5,
                "mod_hp_mult": 4,
                "mana_multiplier": 0,
                "mod_atk_physical": 5,
                "mod_atk_magical": 5,
                "mod_def_physical": 5,
                "mod_def_magical": 5,
                "regen_hp_mod": 1,
                "regen_mana_mod": 0,
            },
        }
        cfg = TransformationConfig.from_dict(data)
        assert cfg.new_name == "X"
        assert cfg.hp_threshold == 0.30


class TestApplyTransformation:

    def test_changes_name(self) -> None:
        boss = _make_char("Old Golem")
        config = _make_transform_config()
        apply_transformation(boss, config)
        assert boss.name == "Awakened Golem"

    def test_changes_modifiers(self) -> None:
        boss = _make_char("Boss")
        config = _make_transform_config()
        old_max_hp = boss.max_hp
        apply_transformation(boss, config)
        assert boss.max_hp != old_max_hp

    def test_heals_boss(self) -> None:
        boss = _make_char("Boss")
        boss.take_damage(boss.current_hp - 1)  # Almost dead
        config = _make_transform_config()
        apply_transformation(boss, config)
        assert boss.current_hp > 1

    def test_heal_pct_of_new_max(self) -> None:
        boss = _make_char("Boss")
        boss.take_damage(boss.current_hp - 1)
        config = _make_transform_config()
        apply_transformation(boss, config)
        expected_heal = int(boss.max_hp * config.heal_pct)
        # Boss should be at least 1 + heal amount
        assert boss.current_hp >= expected_heal

    def test_changes_position(self) -> None:
        boss = _make_char("Boss")
        boss.change_position(Position.BACK)
        config = _make_transform_config()
        apply_transformation(boss, config)
        assert boss.position == Position.FRONT

    def test_should_transform_true_below_threshold(self) -> None:
        boss = _make_char("Boss")
        dmg = boss.current_hp - int(boss.max_hp * 0.25)
        boss.take_damage(dmg)
        config = _make_transform_config()
        ratio = boss.current_hp / boss.max_hp
        assert ratio <= config.hp_threshold

    def test_should_transform_false_above_threshold(self) -> None:
        boss = _make_char("Boss")
        config = _make_transform_config()
        ratio = boss.current_hp / boss.max_hp
        assert ratio > config.hp_threshold
