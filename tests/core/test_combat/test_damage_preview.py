"""Testes para damage_preview — previsão de dano/cura."""

from src.core.combat.damage import DamageType
from src.core.combat.damage_preview import (
    preview_basic_attack,
    preview_heal,
    preview_skill_damage,
)
from src.core.elements.element_type import ElementType
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.skills.skill import Skill
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from src.core.combat.action_economy import ActionType
from tests.core.test_combat.conftest import _build_char


class TestPreviewBasicAttack:

    def test_returns_physical_damage_type(self) -> None:
        attacker = _build_char("A")
        target = _build_char("B")
        result = preview_basic_attack(attacker, target)
        assert result.damage_type == DamageType.PHYSICAL

    def test_min_damage_is_positive(self) -> None:
        attacker = _build_char("A")
        target = _build_char("B")
        result = preview_basic_attack(attacker, target)
        assert result.min_damage >= 1

    def test_max_damage_greater_or_equal_min(self) -> None:
        attacker = _build_char("A")
        target = _build_char("B")
        result = preview_basic_attack(attacker, target)
        assert result.max_damage >= result.min_damage

    def test_crit_chance_is_percentage(self) -> None:
        attacker = _build_char("A")
        target = _build_char("B")
        result = preview_basic_attack(attacker, target)
        assert 0 <= result.crit_chance_pct <= 100


class TestPreviewSkillDamage:

    def _damage_skill(self) -> Skill:
        return Skill(
            skill_id="fireball", name="Fireball", mana_cost=20,
            action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
            slot_cost=3,
            effects=(SkillEffect(
                effect_type=SkillEffectType.DAMAGE,
                base_power=30, element=ElementType.FIRE,
            ),),
        )

    def test_returns_magical_for_elemental(self) -> None:
        attacker = _build_char("A")
        target = _build_char("B")
        result = preview_skill_damage(self._damage_skill(), attacker, target)
        assert result is not None
        assert result.damage_type == DamageType.MAGICAL

    def test_includes_mana_cost(self) -> None:
        attacker = _build_char("A")
        target = _build_char("B")
        result = preview_skill_damage(self._damage_skill(), attacker, target)
        assert result.mana_cost == 20

    def test_returns_none_for_heal_skill(self) -> None:
        heal = Skill(
            skill_id="heal", name="Heal", mana_cost=10,
            action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ALLY,
            slot_cost=2,
            effects=(SkillEffect(
                effect_type=SkillEffectType.HEAL, base_power=20,
            ),),
        )
        result = preview_skill_damage(heal, _build_char("A"), _build_char("B"))
        assert result is None


class TestPreviewHeal:

    def _heal_skill(self) -> Skill:
        return Skill(
            skill_id="heal", name="Heal", mana_cost=15,
            action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ALLY,
            slot_cost=2,
            effects=(SkillEffect(
                effect_type=SkillEffectType.HEAL, base_power=20,
            ),),
        )

    def test_returns_heal_preview(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        target.take_damage(50)
        result = preview_heal(self._heal_skill(), caster, target)
        assert result is not None
        assert result.estimated_heal > 0

    def test_heal_capped_at_missing_hp(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        target.take_damage(10)
        result = preview_heal(self._heal_skill(), caster, target)
        assert result.estimated_heal <= 10

    def test_returns_none_for_damage_skill(self) -> None:
        dmg = Skill(
            skill_id="slash", name="Slash", mana_cost=5,
            action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
            slot_cost=1,
            effects=(SkillEffect(
                effect_type=SkillEffectType.DAMAGE, base_power=10,
            ),),
        )
        result = preview_heal(dmg, _build_char("A"), _build_char("B"))
        assert result is None
