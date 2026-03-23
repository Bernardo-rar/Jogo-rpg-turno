"""Testes para BossTemplate e BossPhaseConfig."""

from __future__ import annotations

from src.core.characters.position import Position
from src.dungeon.enemies.bosses.boss_loader import load_all_bosses, load_boss_template
from src.dungeon.enemies.bosses.boss_template import BossPhaseConfig, BossTemplate
from src.dungeon.enemies.enemy_archetype import EnemyArchetype


class TestBossTemplate:

    def test_from_dict(self) -> None:
        data = {
            "enemy_id": "test_boss",
            "name": "Test Boss",
            "tier": 1,
            "archetype": "DPS",
            "class_modifiers": {
                "hit_dice": 10,
                "mod_hp_flat": 3,
                "mod_hp_mult": 4,
                "mana_multiplier": 1,
                "mod_atk_physical": 6,
                "mod_atk_magical": 2,
                "mod_def_physical": 5,
                "mod_def_magical": 3,
                "regen_hp_mod": 1,
                "regen_mana_mod": 1,
            },
            "base_attributes": {"STRENGTH": 10, "DEXTERITY": 8},
            "position": "FRONT",
            "phases": [
                {
                    "phase_number": 1,
                    "hp_threshold": 0.5,
                    "handler_key": "p1",
                    "skill_ids": ["skill_a"],
                },
                {
                    "phase_number": 2,
                    "hp_threshold": 0.0,
                    "handler_key": "p2",
                    "skill_ids": ["skill_b", "skill_c"],
                },
            ],
            "special_traits": ["boss"],
        }
        template = BossTemplate.from_dict(data)
        assert template.enemy_id == "test_boss"
        assert template.archetype == EnemyArchetype.DPS
        assert len(template.phases) == 2

    def test_all_skill_ids_no_duplicates(self) -> None:
        data = {
            "enemy_id": "test",
            "name": "T",
            "tier": 1,
            "archetype": "TANK",
            "class_modifiers": {
                "hit_dice": 10, "mod_hp_flat": 3, "mod_hp_mult": 4,
                "mana_multiplier": 1, "mod_atk_physical": 6,
                "mod_atk_magical": 2, "mod_def_physical": 5,
                "mod_def_magical": 3, "regen_hp_mod": 1, "regen_mana_mod": 1,
            },
            "base_attributes": {"STRENGTH": 10},
            "position": "FRONT",
            "phases": [
                {"phase_number": 1, "hp_threshold": 0.5, "handler_key": "p1",
                 "skill_ids": ["a", "b"]},
                {"phase_number": 2, "hp_threshold": 0.0, "handler_key": "p2",
                 "skill_ids": ["b", "c"]},
            ],
        }
        template = BossTemplate.from_dict(data)
        ids = template.all_skill_ids()
        assert ids == ("a", "b", "c")


class TestBossPhaseConfig:

    def test_from_dict(self) -> None:
        data = {
            "phase_number": 1,
            "hp_threshold": 0.5,
            "handler_key": "p1",
            "skill_ids": ["x", "y"],
        }
        config = BossPhaseConfig.from_dict(data)
        assert config.phase.handler_key == "p1"
        assert config.skill_ids == ("x", "y")


class TestBossLoader:

    def test_load_goblin_king(self) -> None:
        boss = load_boss_template("goblin_king")
        assert boss.enemy_id == "goblin_king"
        assert len(boss.phases) == 2
        assert "boss" in boss.special_traits

    def test_load_ancient_golem(self) -> None:
        boss = load_boss_template("ancient_golem")
        assert boss.position == Position.FRONT
        assert boss.tier == 2

    def test_load_lich_lord(self) -> None:
        boss = load_boss_template("lich_lord")
        assert boss.position == Position.BACK
        assert "undead" in boss.special_traits

    def test_load_all_bosses(self) -> None:
        bosses = load_all_bosses()
        assert len(bosses) == 3
        assert "goblin_king" in bosses
        assert "ancient_golem" in bosses
        assert "lich_lord" in bosses
