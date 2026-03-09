"""Testes de integracao: SkillBar no Character."""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.action_economy import ActionType
from src.core.skills.cooldown_tracker import CooldownTracker
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType


_MODS = ClassModifiers(
    hit_dice=10, vida_mod=0, mod_hp=5,
    mana_multiplier=6,
    mod_atk_physical=5, mod_atk_magical=5,
    mod_def_physical=3, mod_def_magical=3,
    regen_hp_mod=2, regen_mana_mod=2,
)


def _default_attrs() -> Attributes:
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, 10)
    return attrs


def _default_config(**overrides: object) -> CharacterConfig:
    base: dict[str, object] = {
        "class_modifiers": _MODS,
        "threshold_calculator": ThresholdCalculator({}),
    }
    base.update(overrides)
    return CharacterConfig(**base)  # type: ignore[arg-type]


def _make_skill(skill_id: str, slot_cost: int) -> Skill:
    return Skill(
        skill_id=skill_id, name=skill_id.title(), mana_cost=10,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        effects=(SkillEffect(effect_type=SkillEffectType.DAMAGE, base_power=10),),
        slot_cost=slot_cost,
    )


class TestCharacterSkillBarDefault:
    def test_default_no_skill_bar(self) -> None:
        char = Character("Hero", _default_attrs(), _default_config())
        assert char.skill_bar is None

    def test_with_skill_bar(self) -> None:
        bar = SkillBar(slots=(SpellSlot(max_cost=8),))
        config = _default_config(skill_bar=bar)
        char = Character("Hero", _default_attrs(), config)
        assert char.skill_bar is bar

    def test_skill_bar_has_slots(self) -> None:
        sk = _make_skill("fireball", 5)
        slot = SpellSlot(max_cost=8, skills=(sk,))
        bar = SkillBar(slots=(slot,))
        config = _default_config(skill_bar=bar)
        char = Character("Hero", _default_attrs(), config)
        assert len(char.skill_bar.all_skills) == 1


class TestCharacterSkillBarCooldown:
    def test_cooldown_tracker_accessible(self) -> None:
        bar = SkillBar(slots=())
        config = _default_config(skill_bar=bar)
        char = Character("Hero", _default_attrs(), config)
        assert isinstance(char.skill_bar.cooldown_tracker, CooldownTracker)

    def test_cooldown_functional(self) -> None:
        sk = _make_skill("fireball", 5)
        slot = SpellSlot(max_cost=8, skills=(sk,))
        bar = SkillBar(slots=(slot,))
        config = _default_config(skill_bar=bar)
        char = Character("Hero", _default_attrs(), config)
        char.skill_bar.cooldown_tracker.start_cooldown("fireball", 2)
        assert len(char.skill_bar.ready_skills) == 0


class TestCharacterSkillBarMultipleSlots:
    def test_multiple_slots(self) -> None:
        sk1 = _make_skill("fireball", 5)
        sk2 = _make_skill("heal", 3)
        slot1 = SpellSlot(max_cost=8, skills=(sk1,))
        slot2 = SpellSlot(max_cost=8, skills=(sk2,))
        bar = SkillBar(slots=(slot1, slot2))
        config = _default_config(skill_bar=bar)
        char = Character("Hero", _default_attrs(), config)
        assert len(char.skill_bar.all_skills) == 2

    def test_ready_skills_reflects_cooldowns(self) -> None:
        sk1 = _make_skill("fireball", 5)
        sk2 = _make_skill("heal", 3)
        slot1 = SpellSlot(max_cost=8, skills=(sk1,))
        slot2 = SpellSlot(max_cost=8, skills=(sk2,))
        bar = SkillBar(slots=(slot1, slot2))
        config = _default_config(skill_bar=bar)
        char = Character("Hero", _default_attrs(), config)
        char.skill_bar.cooldown_tracker.start_cooldown("fireball", 1)
        ready_ids = [s.skill_id for s in char.skill_bar.ready_skills]
        assert "heal" in ready_ids
        assert "fireball" not in ready_ids
