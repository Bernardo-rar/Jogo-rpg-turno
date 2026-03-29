"""Testes para EnemyTemplateLoader — carrega JSONs de monstros."""

from src.core.characters.position import Position
from src.dungeon.enemies.enemy_archetype import EnemyArchetype
from src.dungeon.enemies.enemy_template_loader import (
    load_enemy_template,
    load_tier_templates,
)


class TestLoadEnemyTemplate:

    def test_loads_goblin(self) -> None:
        t = load_enemy_template("goblin", tier=1)
        assert t.enemy_id == "goblin"
        assert t.name == "Goblin"

    def test_loads_slime(self) -> None:
        t = load_enemy_template("slime", tier=1)
        assert t.archetype is EnemyArchetype.TANK

    def test_loads_mushroom_position_back(self) -> None:
        t = load_enemy_template("mushroom", tier=1)
        assert t.position is Position.BACK

    def test_loads_skeleton_with_skill(self) -> None:
        t = load_enemy_template("skeleton", tier=1)
        assert "bone_shield" in t.skill_ids

    def test_loads_rat_swarm_traits(self) -> None:
        t = load_enemy_template("rat_swarm", tier=1)
        assert "multi_hit" in t.special_traits


class TestLoadTierTemplates:

    def test_tier1_has_monsters(self) -> None:
        templates = load_tier_templates(tier=1)
        assert len(templates) >= 5

    def test_tier1_contains_original_enemies(self) -> None:
        templates = load_tier_templates(tier=1)
        original = {"goblin", "slime", "rat_swarm", "skeleton", "mushroom"}
        assert original.issubset(set(templates.keys()))

    def test_all_templates_are_tier_1(self) -> None:
        templates = load_tier_templates(tier=1)
        for t in templates.values():
            assert t.tier == 1
