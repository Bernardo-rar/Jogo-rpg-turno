"""Testes para EliteModifier — transformação de EnemyTemplate em Elite."""

from __future__ import annotations

from random import Random

from src.core.attributes.attribute_types import AttributeType
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.dungeon.enemies.elite_modifier import (
    EliteTierBonuses,
    apply_elite,
    load_elite_bonuses,
)
from src.dungeon.enemies.enemy_archetype import EnemyArchetype
from src.dungeon.enemies.enemy_template import EnemyTemplate

_BASE_MODS = ClassModifiers(
    hit_dice=8,
    mod_hp_flat=2,
    mod_hp_mult=2,
    mana_multiplier=1,
    mod_atk_physical=5,
    mod_atk_magical=2,
    mod_def_physical=4,
    mod_def_magical=3,
    regen_hp_mod=1,
    regen_mana_mod=1,
)

_BASE_TEMPLATE = EnemyTemplate(
    enemy_id="goblin",
    name="Goblin",
    tier=1,
    archetype=EnemyArchetype.DPS,
    class_modifiers=_BASE_MODS,
    base_attributes={
        AttributeType.STRENGTH: 6,
        AttributeType.DEXTERITY: 8,
    },
    position=Position.FRONT,
    elemental_profile_id="goblin_profile",
    weapon_id="dagger",
    skill_ids=("goblin_rally",),
    special_traits=("pack_tactics",),
)

_TIER1_BONUSES = EliteTierBonuses(
    bonus_skill_pool=("elite_regen", "elite_thorns", "elite_evasion"),
    bonus_count=1,
    stat_scale_min=1.3,
    stat_scale_max=1.4,
)


class TestApplyElite:

    def test_name_has_elite_prefix(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        assert result.name.startswith("Elite ")
        assert "Goblin" in result.name

    def test_stats_are_scaled_up(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        assert result.class_modifiers.hit_dice > _BASE_MODS.hit_dice
        assert result.class_modifiers.mod_atk_physical > _BASE_MODS.mod_atk_physical
        assert result.class_modifiers.mod_def_physical > _BASE_MODS.mod_def_physical

    def test_stats_within_scale_range(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        min_atk = _BASE_MODS.mod_atk_physical * _TIER1_BONUSES.stat_scale_min
        max_atk = _BASE_MODS.mod_atk_physical * _TIER1_BONUSES.stat_scale_max
        # ceil pode dar +1 acima do max range
        assert result.class_modifiers.mod_atk_physical >= int(min_atk)
        assert result.class_modifiers.mod_atk_physical <= int(max_atk) + 1

    def test_non_scalable_fields_preserved(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        assert result.class_modifiers.mana_multiplier == _BASE_MODS.mana_multiplier
        assert result.class_modifiers.regen_hp_mod == _BASE_MODS.regen_hp_mod
        assert result.class_modifiers.regen_mana_mod == _BASE_MODS.regen_mana_mod
        assert (
            result.class_modifiers.preferred_attack_type
            == _BASE_MODS.preferred_attack_type
        )

    def test_bonus_skill_added(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        original_ids = set(_BASE_TEMPLATE.skill_ids)
        elite_ids = set(result.skill_ids)
        new_ids = elite_ids - original_ids
        assert len(new_ids) == _TIER1_BONUSES.bonus_count

    def test_bonus_skill_from_pool(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        original_ids = set(_BASE_TEMPLATE.skill_ids)
        new_ids = set(result.skill_ids) - original_ids
        assert new_ids.issubset(set(_TIER1_BONUSES.bonus_skill_pool))

    def test_elite_trait_added(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        assert "elite" in result.special_traits

    def test_original_traits_preserved(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        assert "pack_tactics" in result.special_traits

    def test_immutable_fields_unchanged(self) -> None:
        result = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(42))
        assert result.enemy_id == _BASE_TEMPLATE.enemy_id
        assert result.tier == _BASE_TEMPLATE.tier
        assert result.archetype == _BASE_TEMPLATE.archetype
        assert result.position == _BASE_TEMPLATE.position
        assert result.weapon_id == _BASE_TEMPLATE.weapon_id
        assert result.base_attributes == _BASE_TEMPLATE.base_attributes

    def test_deterministic_with_seed(self) -> None:
        r1 = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(99))
        r2 = apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(99))
        assert r1.class_modifiers == r2.class_modifiers
        assert r1.skill_ids == r2.skill_ids

    def test_different_seeds_can_vary(self) -> None:
        results = [
            apply_elite(_BASE_TEMPLATE, _TIER1_BONUSES, Random(i))
            for i in range(20)
        ]
        hit_dices = {r.class_modifiers.hit_dice for r in results}
        assert len(hit_dices) >= 2


class TestEliteTierBonuses:

    def test_from_dict(self) -> None:
        data = {
            "bonus_skill_pool": ["a", "b"],
            "bonus_count": 1,
            "stat_scale_min": 1.3,
            "stat_scale_max": 1.4,
        }
        bonuses = EliteTierBonuses.from_dict(data)
        assert bonuses.bonus_count == 1
        assert len(bonuses.bonus_skill_pool) == 2


class TestLoadEliteBonuses:

    def test_loads_tier1(self) -> None:
        bonuses = load_elite_bonuses()
        assert 1 in bonuses

    def test_all_tiers_have_pool(self) -> None:
        bonuses = load_elite_bonuses()
        for tier_bonus in bonuses.values():
            assert len(tier_bonus.bonus_skill_pool) > 0

    def test_scale_ranges_valid(self) -> None:
        bonuses = load_elite_bonuses()
        for tier_bonus in bonuses.values():
            assert tier_bonus.stat_scale_min < tier_bonus.stat_scale_max
            assert tier_bonus.stat_scale_min >= 1.0
