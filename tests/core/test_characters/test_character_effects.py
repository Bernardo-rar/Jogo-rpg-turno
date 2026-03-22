"""Testes para integracao Character + EffectManager + ElementalProfile."""

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.effects.buff_factory import (
    create_flat_buff,
    create_flat_debuff,
    create_percent_buff,
    create_percent_debuff,
)
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile

FIGHTER_MODS = ClassModifiers(
    hit_dice=12,
    mod_hp_flat=0,
    mod_hp_mult=10,
    mana_multiplier=6,
    mod_atk_physical=10,
    mod_atk_magical=6,
    mod_def_physical=5,
    mod_def_magical=3,
    regen_hp_mod=5,
    regen_mana_mod=3,
)


@pytest.fixture
def attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 10,
        AttributeType.DEXTERITY: 8,
        AttributeType.CONSTITUTION: 5,
        AttributeType.INTELLIGENCE: 3,
        AttributeType.WISDOM: 4,
        AttributeType.CHARISMA: 3,
        AttributeType.MIND: 4,
    })


@pytest.fixture
def threshold_calc() -> ThresholdCalculator:
    return ThresholdCalculator.from_json("data/attributes/thresholds.json")


@pytest.fixture
def character(attrs, threshold_calc) -> Character:
    config = CharacterConfig(
        class_modifiers=FIGHTER_MODS,
        threshold_calculator=threshold_calc,
    )
    return Character(
        name="TestHero",
        attributes=attrs,
        config=config,
    )


class TestCharacterEffectManager:

    def test_character_has_effect_manager(self, character) -> None:
        assert isinstance(character.effect_manager, EffectManager)

    def test_character_has_elemental_profile(self, character) -> None:
        assert isinstance(character.elemental_profile, ElementalProfile)

    def test_default_elemental_profile_is_neutral(self, character) -> None:
        profile = character.elemental_profile
        assert profile.get_multiplier(ElementType.FIRE) == 1.0

    def test_custom_elemental_profile_injected(
        self, attrs, threshold_calc,
    ) -> None:
        profile = ElementalProfile(
            resistances={ElementType.FIRE: 0.5},
        )
        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
            elemental_profile=profile,
        )
        char = Character(
            name="FireRes",
            attributes=attrs,
            config=config,
        )
        assert char.elemental_profile.is_resistant_to(ElementType.FIRE)


class TestStatModifiersFromEffects:

    def test_physical_attack_with_flat_buff(self, character) -> None:
        base = character.physical_attack
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 10, 3)
        character.effect_manager.add_effect(buff)
        assert character.physical_attack == base + 10

    def test_physical_attack_with_percent_buff(self, character) -> None:
        base = character.physical_attack
        buff = create_percent_buff(ModifiableStat.PHYSICAL_ATTACK, 20.0, 3)
        character.effect_manager.add_effect(buff)
        expected = int(base * 1.2)
        assert character.physical_attack == expected

    def test_magical_attack_with_buff(self, character) -> None:
        base = character.magical_attack
        buff = create_flat_buff(ModifiableStat.MAGICAL_ATTACK, 5, 3)
        character.effect_manager.add_effect(buff)
        assert character.magical_attack == base + 5

    def test_physical_defense_with_debuff(self, character) -> None:
        base = character.physical_defense
        debuff = create_flat_debuff(ModifiableStat.PHYSICAL_DEFENSE, 5, 3)
        character.effect_manager.add_effect(debuff)
        assert character.physical_defense == base - 5

    def test_magical_defense_with_debuff(self, character) -> None:
        base = character.magical_defense
        debuff = create_flat_debuff(ModifiableStat.MAGICAL_DEFENSE, 3, 3)
        character.effect_manager.add_effect(debuff)
        assert character.magical_defense == base - 3

    def test_speed_with_modifier(self, character) -> None:
        base = character.speed
        buff = create_flat_buff(ModifiableStat.SPEED, 5, 3)
        character.effect_manager.add_effect(buff)
        assert character.speed == base + 5

    def test_max_hp_with_modifier(self, character) -> None:
        base = character.max_hp
        buff = create_flat_buff(ModifiableStat.MAX_HP, 20, 3)
        character.effect_manager.add_effect(buff)
        assert character.max_hp == base + 20

    def test_hp_regen_with_modifier(self, character) -> None:
        base = character.hp_regen
        buff = create_flat_buff(ModifiableStat.HP_REGEN, 3, 3)
        character.effect_manager.add_effect(buff)
        assert character.hp_regen == base + 3

    def test_mana_regen_with_modifier(self, character) -> None:
        base = character.mana_regen
        buff = create_flat_buff(ModifiableStat.MANA_REGEN, 2, 3)
        character.effect_manager.add_effect(buff)
        assert character.mana_regen == base + 2

    def test_multiple_effects_stack(self, character) -> None:
        base = character.physical_attack
        from src.core.effects.stacking import StackingPolicy
        character.effect_manager.set_stacking_policy(
            "buff_physical_attack", StackingPolicy.STACK,
        )
        buff1 = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 5, 3)
        buff2 = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 7, 3)
        character.effect_manager.add_effect(buff1)
        character.effect_manager.add_effect(buff2)
        assert character.physical_attack == base + 12

    def test_modifier_gone_after_expiry(self, character) -> None:
        base = character.physical_attack
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 10, 1)
        character.effect_manager.add_effect(buff)
        assert character.physical_attack == base + 10
        character.effect_manager.tick_all()
        assert character.physical_attack == base

    def test_max_mana_with_flat_buff(self, character) -> None:
        base = character.max_mana
        buff = create_flat_buff(ModifiableStat.MAX_MANA, 50, 3)
        character.effect_manager.add_effect(buff)
        assert character.max_mana == base + 50

    def test_max_mana_with_percent_debuff(self, character) -> None:
        base = character.max_mana
        debuff = create_percent_debuff(ModifiableStat.MAX_MANA, 25.0, 3)
        character.effect_manager.add_effect(debuff)
        expected = int(base * 0.75)
        assert character.max_mana == expected

    def test_negative_stat_floors_at_zero(self, character) -> None:
        debuff = create_flat_debuff(ModifiableStat.PHYSICAL_ATTACK, 9999, 3)
        character.effect_manager.add_effect(debuff)
        assert character.physical_attack >= 0


class TestSubclassEffectInteraction:

    def test_fighter_attack_with_buff_and_stance(
        self, attrs, threshold_calc,
    ) -> None:
        from src.core.classes.fighter.fighter import Fighter
        from src.core.classes.fighter.stance import Stance

        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
        )
        fighter = Fighter(
            name="TestFighter",
            attributes=attrs,
            config=config,
        )
        fighter.change_stance(Stance.OFFENSIVE)
        base_with_stance = fighter.physical_attack
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 10, 3)
        fighter.effect_manager.add_effect(buff)
        buffed_with_stance = fighter.physical_attack
        assert buffed_with_stance > base_with_stance

    def test_mage_magical_attack_with_buff_and_overcharge(
        self, attrs, threshold_calc,
    ) -> None:
        from src.core.classes.mage.mage import Mage

        mage_mods = ClassModifiers(
            hit_dice=6,
            mod_hp_flat=0,
            mod_hp_mult=4,
            mana_multiplier=12,
            mod_atk_physical=4,
            mod_atk_magical=10,
            mod_def_physical=2,
            mod_def_magical=6,
            regen_hp_mod=2,
            regen_mana_mod=5,
        )
        config = CharacterConfig(
            class_modifiers=mage_mods,
            threshold_calculator=threshold_calc,
            position=Position.BACK,
        )
        mage = Mage(
            name="TestMage",
            attributes=attrs,
            config=config,
        )
        mage.activate_overcharge()
        base_with_overcharge = mage.magical_attack
        buff = create_flat_buff(ModifiableStat.MAGICAL_ATTACK, 10, 3)
        mage.effect_manager.add_effect(buff)
        buffed_with_overcharge = mage.magical_attack
        assert buffed_with_overcharge > base_with_overcharge


class TestHealingReceivedModifiers:

    def test_heal_applies_healing_received_buff(self, character) -> None:
        character.take_damage(200)
        buff = create_percent_buff(ModifiableStat.HEALING_RECEIVED, 50.0, 3)
        character.effect_manager.add_effect(buff)
        healed = character.heal(100)
        assert healed > 100

    def test_heal_applies_healing_received_debuff(self, character) -> None:
        character.take_damage(200)
        debuff = create_percent_debuff(ModifiableStat.HEALING_RECEIVED, 50.0, 3)
        character.effect_manager.add_effect(debuff)
        healed = character.heal(100)
        assert healed < 100
