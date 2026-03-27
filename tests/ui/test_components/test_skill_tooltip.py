"""Testes para skill_tooltip — logica de montagem de linhas do tooltip."""

from dataclasses import dataclass

from src.core.combat.action_economy import ActionType
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.skills.resource_cost import ResourceCost
from src.core.skills.skill import Skill
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from src.ui.components.skill_tooltip import build_skill_info_lines


@dataclass
class _FakeCaster:
    """Caster minimo para testes de tooltip."""

    physical_attack: int = 10
    magical_attack: int = 15


def _damage_skill() -> Skill:
    return Skill(
        skill_id="fireball", name="Fireball", mana_cost=20,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        slot_cost=1, description="A ball of fire.",
        cooldown_turns=2,
        effects=(SkillEffect(
            effect_type=SkillEffectType.DAMAGE,
            base_power=30, element=ElementType.FIRE,
        ),),
    )


def _heal_skill() -> Skill:
    return Skill(
        skill_id="heal", name="Heal", mana_cost=15,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ALLY,
        slot_cost=1, description="Restores HP.",
        effects=(SkillEffect(
            effect_type=SkillEffectType.HEAL,
            base_power=25,
        ),),
    )


def _buff_skill() -> Skill:
    return Skill(
        skill_id="shield_of_faith", name="Shield of Faith", mana_cost=10,
        action_type=ActionType.BONUS_ACTION, target_type=TargetType.SINGLE_ALLY,
        slot_cost=1,
        effects=(SkillEffect(
            effect_type=SkillEffectType.BUFF,
            base_power=5, stat=ModifiableStat.PHYSICAL_DEFENSE,
            duration=3,
        ),),
    )


def _skill_with_resource() -> Skill:
    return Skill(
        skill_id="raging_blow", name="Raging Blow", mana_cost=0,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        slot_cost=1,
        resource_costs=(ResourceCost(resource_type="fury_bar", amount=20),),
        effects=(SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=40,
        ),),
    )


def _ailment_skill() -> Skill:
    return Skill(
        skill_id="poison_strike", name="Poison Strike", mana_cost=5,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        slot_cost=1,
        effects=(
            SkillEffect(
                effect_type=SkillEffectType.DAMAGE, base_power=10,
            ),
            SkillEffect(
                effect_type=SkillEffectType.APPLY_AILMENT,
                ailment_id="poison",
            ),
        ),
    )


class TestBuildDamageSkillLines:

    def test_first_line_is_skill_name(self) -> None:
        lines = build_skill_info_lines(_damage_skill(), _FakeCaster())
        assert lines[0][0] == "Fireball"

    def test_description_present(self) -> None:
        lines = build_skill_info_lines(_damage_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert "A ball of fire." in texts

    def test_mana_cost_present(self) -> None:
        lines = build_skill_info_lines(_damage_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert "Mana: 20" in texts

    def test_damage_estimate_present(self) -> None:
        lines = build_skill_info_lines(_damage_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        # base_power=30 + magical_attack=15 = 45
        assert "Damage: ~45" in texts

    def test_cooldown_present(self) -> None:
        lines = build_skill_info_lines(_damage_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert "Cooldown: 2 turns" in texts

    def test_element_present(self) -> None:
        lines = build_skill_info_lines(_damage_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert "Element: Fire" in texts

    def test_damage_color_is_red(self) -> None:
        lines = build_skill_info_lines(_damage_skill(), _FakeCaster())
        damage_line = next(l for l in lines if l[0].startswith("Damage:"))
        assert damage_line[1] == (255, 80, 80)


class TestBuildHealSkillLines:

    def test_heal_estimate_present(self) -> None:
        lines = build_skill_info_lines(_heal_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        # base_power=25 + magical_attack=15 = 40
        assert "Heal: ~40" in texts

    def test_heal_color_is_green(self) -> None:
        lines = build_skill_info_lines(_heal_skill(), _FakeCaster())
        heal_line = next(l for l in lines if l[0].startswith("Heal:"))
        assert heal_line[1] == (80, 255, 80)

    def test_no_cooldown_when_zero(self) -> None:
        lines = build_skill_info_lines(_heal_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert not any("Cooldown" in t for t in texts)

    def test_no_element_when_none(self) -> None:
        lines = build_skill_info_lines(_heal_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert not any("Element" in t for t in texts)


class TestBuildResourceCostLines:

    def test_resource_cost_present(self) -> None:
        lines = build_skill_info_lines(_skill_with_resource(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert "Fury: 20" in texts

    def test_resource_color_is_orange(self) -> None:
        lines = build_skill_info_lines(_skill_with_resource(), _FakeCaster())
        fury_line = next(l for l in lines if "Fury" in l[0])
        assert fury_line[1] == (255, 180, 50)

    def test_zero_mana_cost_skipped(self) -> None:
        lines = build_skill_info_lines(_skill_with_resource(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert not any("Mana" in t for t in texts)


class TestBuildBuffSkillLines:

    def test_buff_line_format(self) -> None:
        lines = build_skill_info_lines(_buff_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert "+5 Physical_Defense (3 turns)" in texts

    def test_buff_color_is_cyan(self) -> None:
        lines = build_skill_info_lines(_buff_skill(), _FakeCaster())
        buff_line = next(l for l in lines if l[0].startswith("+"))
        assert buff_line[1] == (80, 255, 255)


class TestBuildAilmentSkillLines:

    def test_ailment_line_present(self) -> None:
        lines = build_skill_info_lines(_ailment_skill(), _FakeCaster())
        texts = [t for t, _ in lines]
        assert "Applies: poison" in texts

    def test_ailment_color_is_purple(self) -> None:
        lines = build_skill_info_lines(_ailment_skill(), _FakeCaster())
        ailment_line = next(l for l in lines if l[0].startswith("Applies:"))
        assert ailment_line[1] == (200, 100, 255)


class TestBuildPhysicalDamageEstimate:

    def test_physical_uses_physical_attack(self) -> None:
        """Skill sem elemento usa physical_attack do caster."""
        lines = build_skill_info_lines(_skill_with_resource(), _FakeCaster())
        texts = [t for t, _ in lines]
        # base_power=40 + physical_attack=10 = 50
        assert "Damage: ~50" in texts
