"""Testes de wiring: combo elemental integrado ao fluxo de dano."""

from __future__ import annotations

from src.core.combat.combat_engine import EventType
from src.core.combat.skill_effect_applier import (
    apply_skill_effect,
    get_combo_detector,
    set_combo_detector,
)
from src.core.elements.combo.combo_config import ComboConfig, ComboEffect
from src.core.elements.combo.combo_detector import ComboDetector
from src.core.elements.combo.element_marker import ElementMarker
from src.core.elements.element_type import ElementType
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType

from tests.core.test_combat.conftest import _build_char


def _make_fire_ice_detector() -> ComboDetector:
    """Cria detector com combo FIRE+ICE para testes."""
    combo = ComboConfig(
        combo_name="Freeze Burst",
        element_a=ElementType.FIRE,
        element_b=ElementType.ICE,
        effect=ComboEffect(
            ailment_id="freeze",
            ailment_duration=3,
            bonus_damage=15,
        ),
    )
    combos = {frozenset({ElementType.FIRE, ElementType.ICE}): combo}
    return ComboDetector(combos=combos)


class TestElementalDamageAddsMarker:
    def test_elemental_damage_adds_marker_to_target(self) -> None:
        """Dano elemental deve adicionar ElementMarker ao alvo."""
        set_combo_detector(None)
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE,
            base_power=20,
            element=ElementType.FIRE,
        )

        apply_skill_effect(effect, [target], 1, caster)

        assert target.effect_manager.has_effect("element_marker_FIRE")

    def test_non_elemental_damage_no_marker(self) -> None:
        """Dano sem elemento NAO deve adicionar marker."""
        set_combo_detector(None)
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE,
            base_power=20,
        )

        apply_skill_effect(effect, [target], 1, caster)

        effects = target.effect_manager.active_effects
        markers = [e for e in effects if isinstance(e, ElementMarker)]
        assert len(markers) == 0


class TestComboTriggersOnDamage:
    def test_combo_triggers_when_two_elements_hit(self) -> None:
        """FIRE marker + ICE damage deve disparar combo e aplicar bonus."""
        detector = _make_fire_ice_detector()
        set_combo_detector(detector)
        caster = _build_char("Caster")
        target = _build_char("Target")

        # Primeiro hit: FIRE — adiciona marker
        fire_effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE,
            base_power=10,
            element=ElementType.FIRE,
        )
        apply_skill_effect(fire_effect, [target], 1, caster)
        hp_after_fire = target.current_hp

        # Segundo hit: ICE — deve disparar combo
        ice_effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE,
            base_power=10,
            element=ElementType.ICE,
        )
        events = apply_skill_effect(ice_effect, [target], 1, caster)

        # Combo deve ter causado dano bonus alem do dano normal
        assert target.current_hp < hp_after_fire
        # Deve haver evento de combo alem do evento de dano normal
        combo_events = [
            e for e in events if e.description == "Freeze Burst"
        ]
        assert len(combo_events) == 1
        assert combo_events[0].event_type == EventType.DAMAGE

        # Cleanup
        set_combo_detector(None)

    def test_no_combo_without_detector(self) -> None:
        """Sem detector configurado, combo nao dispara."""
        set_combo_detector(None)
        caster = _build_char("Caster")
        target = _build_char("Target")

        # Adiciona marker manualmente
        target.effect_manager.add_effect(ElementMarker(ElementType.FIRE))

        ice_effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE,
            base_power=10,
            element=ElementType.ICE,
        )
        events = apply_skill_effect(ice_effect, [target], 1, caster)

        # Apenas evento de dano normal, sem combo
        combo_events = [
            e for e in events if e.description == "Freeze Burst"
        ]
        assert len(combo_events) == 0


class TestComboDetectorAccessors:
    def test_set_and_get_combo_detector(self) -> None:
        """set/get_combo_detector devem funcionar corretamente."""
        detector = _make_fire_ice_detector()
        set_combo_detector(detector)
        assert get_combo_detector() is detector
        set_combo_detector(None)
        assert get_combo_detector() is None
