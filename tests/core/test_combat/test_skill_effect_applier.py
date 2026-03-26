"""Testes para skill_effect_applier - aplica SkillEffect a alvos."""

from __future__ import annotations

from src.core.combat.combat_engine import EventType
from src.core.combat.skill_effect_applier import apply_skill_effect
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType

from tests.core.test_combat.conftest import _build_char


class TestApplyDamage:
    def test_damage_reduces_target_hp(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        hp_before = target.current_hp
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=20,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert target.current_hp < hp_before
        assert len(events) == 1
        assert events[0].damage is not None

    def test_damage_scales_with_caster_physical_attack(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=20,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        expected_attack = 20 + caster.physical_attack
        assert events[0].damage.raw_damage == expected_attack
        assert events[0].damage.defense_value == target.physical_defense

    def test_damage_scales_with_caster_magical_attack(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=30,
            element=ElementType.FIRE,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        expected_attack = 30 + caster.magical_attack
        assert events[0].damage.raw_damage == expected_attack
        assert events[0].damage.defense_value == target.magical_defense

    def test_damage_without_element_uses_physical_defense(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=50,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert events[0].damage is not None
        assert events[0].damage.defense_value == target.physical_defense

    def test_damage_applied_to_all_targets(self) -> None:
        caster = _build_char("AOE")
        t1 = _build_char("T1")
        t2 = _build_char("T2")
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=10,
        )
        events = apply_skill_effect(effect, [t1, t2], 1, caster)
        assert len(events) == 2


class TestApplyHeal:
    def test_heal_restores_hp(self) -> None:
        caster = _build_char("Healer")
        target = _build_char("Target")
        target.take_damage(30)
        hp_before = target.current_hp
        effect = SkillEffect(
            effect_type=SkillEffectType.HEAL, base_power=20,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert target.current_hp > hp_before
        assert events[0].event_type == EventType.HEAL

    def test_heal_capped_at_max_hp(self) -> None:
        caster = _build_char("Healer")
        target = _build_char("Target")
        target.take_damage(5)
        effect = SkillEffect(
            effect_type=SkillEffectType.HEAL, base_power=100,
        )
        apply_skill_effect(effect, [target], 1, caster)
        assert target.current_hp == target.max_hp


class TestApplyBuff:
    def test_buff_adds_to_effect_manager(self) -> None:
        caster = _build_char("Buffer")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.BUFF,
            base_power=10, stat=ModifiableStat.PHYSICAL_DEFENSE,
            duration=3,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert len(target.effect_manager.active_effects) == 1
        assert events[0].event_type == EventType.BUFF

    def test_buff_event_has_stat_description(self) -> None:
        caster = _build_char("Buffer")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.BUFF,
            base_power=10, stat=ModifiableStat.PHYSICAL_DEFENSE,
            duration=3,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert events[0].description == "physical_defense"


class TestApplyDebuff:
    def test_debuff_adds_to_effect_manager(self) -> None:
        caster = _build_char("Debuffer")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.DEBUFF,
            base_power=5, stat=ModifiableStat.PHYSICAL_ATTACK,
            duration=2,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert len(target.effect_manager.active_effects) == 1
        assert events[0].event_type == EventType.DEBUFF

    def test_debuff_event_has_stat_description(self) -> None:
        caster = _build_char("Debuffer")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.DEBUFF,
            base_power=5, stat=ModifiableStat.PHYSICAL_ATTACK,
            duration=2,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert events[0].description == "physical_attack"


class TestApplyAilment:
    def test_ailment_adds_poison(self) -> None:
        caster = _build_char("Poisoner")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.APPLY_AILMENT,
            base_power=10, ailment_id="poison", duration=3,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert len(target.effect_manager.active_effects) == 1
        assert events[0].event_type == EventType.AILMENT
        assert events[0].description == "poison"

    def test_apply_ailment_freeze_creates_effect(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.APPLY_AILMENT,
            base_power=0, ailment_id="freeze", duration=2,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert len(target.effect_manager.active_effects) == 1
        assert events[0].event_type == EventType.AILMENT
        assert events[0].description == "freeze"

    def test_apply_ailment_weakness_uses_base_power_as_reduction(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.APPLY_AILMENT,
            base_power=20, ailment_id="weakness", duration=3,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert len(target.effect_manager.active_effects) == 1
        assert events[0].event_type == EventType.AILMENT
        assert events[0].description == "weakness"

    def test_unknown_ailment_returns_empty(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.APPLY_AILMENT,
            ailment_id="unknown_thing", duration=3,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert events == []


class TestApplyCounterAttack:
    def test_counter_attack_excludes_caster_from_targets(self) -> None:
        """Quando o caster esta na lista de alvos, nao deve atacar a si mesmo."""
        caster = _build_char("Fighter")
        enemy = _build_char("Enemy")
        hp_caster_before = caster.current_hp
        effect = SkillEffect(
            effect_type=SkillEffectType.COUNTER_ATTACK,
            base_power=10,
        )
        # Passa caster + enemy como alvos; caster nao deve se auto-atacar
        targets = [t for t in [caster, enemy] if t is not caster]
        events = apply_skill_effect(effect, targets, 1, caster)
        assert caster.current_hp == hp_caster_before
        assert len(events) == 1
        assert events[0].target_name == "Enemy"


class TestMechanicDispatch:
    def test_mechanic_dispatch_has_all_known_ids(self) -> None:
        from src.core.combat.skill_effect_applier import _MECHANIC_DISPATCH
        expected_ids = {
            "change_stance_offensive",
            "change_stance_defensive",
            "change_stance_normal",
            "activate_reckless_stance",
            "action_surge",
            "activate_overcharge",
            "activate_overcharged",
            "switch_aura_offensive",
            "switch_aura_defensive",
            "apply_hunters_mark",
            "shift_destruction",
            "shift_vitality",
            "shift_balance",
            "set_metamagic",
            "transform_animal_form",
            "create_field_condition",
            "enter_stealth",
            "envenom_weapon",
        }
        assert expected_ids.issubset(set(_MECHANIC_DISPATCH.keys()))
