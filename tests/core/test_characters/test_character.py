import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import (
    BONUS_ATK_PHYSICAL,
    BONUS_DEF_PHYSICAL,
    BONUS_HP,
    ThresholdCalculator,
)
from src.core.characters.character import CON_HEAL_BONUS_PER_POINT, Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.effects.buff_factory import create_flat_buff
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat

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
def fighter_attrs() -> Attributes:
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
def fighter(fighter_attrs, threshold_calc) -> Character:
    config = CharacterConfig(
        class_modifiers=FIGHTER_MODS,
        threshold_calculator=threshold_calc,
    )
    return Character(name="Roland", attributes=fighter_attrs, config=config)


class TestCharacterCreation:
    def test_character_has_name(self, fighter: Character):
        assert fighter.name == "Roland"

    def test_character_default_level_is_1(self, fighter: Character):
        assert fighter.level == 1

    def test_character_default_position_is_front(self, fighter: Character):
        assert fighter.position == Position.FRONT

    def test_character_starts_alive(self, fighter: Character):
        assert fighter.is_alive is True

    def test_character_with_custom_level(self, fighter_attrs, threshold_calc):
        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
            level=5,
        )
        char = Character(name="Roland", attributes=fighter_attrs, config=config)
        assert char.level == 5

    def test_character_with_back_position(self, fighter_attrs, threshold_calc):
        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
            position=Position.BACK,
        )
        char = Character(name="Gandalf", attributes=fighter_attrs, config=config)
        assert char.position == Position.BACK


class TestCharacterHp:
    def test_max_hp_level_1_fighter(self, fighter: Character):
        # ((hit_dice + CON + mod_hp_flat) * 2) * mod_hp_mult
        # ((12 + 5 + 0) * 2) * 10 = 340
        assert fighter.max_hp == 340

    def test_max_hp_level_2_accumulates(self, fighter_attrs, threshold_calc):
        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
            level=2,
        )
        char = Character(name="Roland", attributes=fighter_attrs, config=config)
        # base * (level + 1) * mod_hp_mult = 17 * 3 * 10 = 510
        assert char.max_hp == 510

    def test_current_hp_starts_at_max(self, fighter: Character):
        assert fighter.current_hp == fighter.max_hp


class TestCharacterMana:
    def test_max_mana_fighter_level_1(self, fighter: Character):
        # mana_multiplier * MIND * 5 = 6 * 4 * 5 = 120
        assert fighter.max_mana == 120

    def test_current_mana_starts_at_max(self, fighter: Character):
        assert fighter.current_mana == fighter.max_mana


class TestCharacterAttack:
    def test_physical_attack_no_weapon(self, fighter: Character):
        # (weapon_die=0 + STR + DEX) * mod_atk_physical
        # (0 + 10 + 8) * 10 = 180
        assert fighter.physical_attack == 180

    def test_magical_attack_no_weapon(self, fighter: Character):
        # (weapon_die=0 + WIS + INT) * mod_atk_magical
        # (0 + 4 + 3) * 6 = 42
        assert fighter.magical_attack == 42


class TestCharacterSpeed:
    def test_speed_equals_dexterity(self, fighter: Character):
        # Speed = DEX = 8
        assert fighter.speed == 8


class TestCharacterDefense:
    def test_physical_defense(self, fighter: Character):
        # (DEX + CON + STR) * mod_def_physical
        # (8 + 5 + 10) * 5 = 115
        assert fighter.physical_defense == 115

    def test_magical_defense(self, fighter: Character):
        # (CON + WIS + INT) * mod_def_magical
        # (5 + 4 + 3) * 3 = 36
        assert fighter.magical_defense == 36


class TestCharacterRegen:
    def test_hp_regen(self, fighter: Character):
        # CON * regen_hp_mod = 5 * 5 = 25
        assert fighter.hp_regen == 25

    def test_mana_regen(self, fighter: Character):
        # MIND * regen_mana_mod = 4 * 3 = 12
        assert fighter.mana_regen == 12


class TestCharacterTakeDamage:
    def test_take_damage_reduces_hp(self, fighter: Character):
        fighter.take_damage(100)
        assert fighter.current_hp == fighter.max_hp - 100

    def test_take_damage_returns_actual_damage(self, fighter: Character):
        actual = fighter.take_damage(100)
        assert actual == 100

    def test_take_damage_cannot_go_below_zero(self, fighter: Character):
        fighter.take_damage(9999)
        assert fighter.current_hp == 0

    def test_take_damage_returns_clamped_damage(self, fighter: Character):
        actual = fighter.take_damage(9999)
        assert actual == fighter.max_hp

    def test_take_damage_to_zero_kills(self, fighter: Character):
        fighter.take_damage(9999)
        assert fighter.is_alive is False


class TestCharacterHeal:
    def test_heal_restores_hp(self, fighter: Character):
        fighter.take_damage(100)
        healed = fighter.heal(50)
        # CON=5, heal(50) -> int(50 * (1 + 5*0.05)) = int(50 * 1.25) = 62
        con = 5
        expected_heal = int(50 * (1 + con * CON_HEAL_BONUS_PER_POINT))
        assert fighter.current_hp == fighter.max_hp - 100 + expected_heal
        assert healed == expected_heal

    def test_heal_cannot_exceed_max(self, fighter: Character):
        fighter.take_damage(10)
        healed = fighter.heal(100)
        assert fighter.current_hp == fighter.max_hp
        assert healed == 10

    def test_heal_does_not_revive_dead(self, fighter: Character):
        fighter.take_damage(9999)
        healed = fighter.heal(100)
        assert fighter.current_hp == 0
        assert fighter.is_alive is False
        assert healed == 0


class TestCharacterManaSpend:
    def test_spend_mana_reduces_current(self, fighter: Character):
        result = fighter.spend_mana(50)
        assert result is True
        assert fighter.current_mana == fighter.max_mana - 50

    def test_spend_mana_fails_if_insufficient(self, fighter: Character):
        result = fighter.spend_mana(9999)
        assert result is False
        assert fighter.current_mana == fighter.max_mana

    def test_restore_mana_increases_current(self, fighter: Character):
        fighter.spend_mana(100)
        restored = fighter.restore_mana(50)
        assert restored == 50
        assert fighter.current_mana == fighter.max_mana - 50

    def test_restore_mana_cannot_exceed_max(self, fighter: Character):
        fighter.spend_mana(10)
        restored = fighter.restore_mana(100)
        assert restored == 10
        assert fighter.current_mana == fighter.max_mana


class TestCharacterManaDrain:
    def test_drain_mana_reduces_current(self, fighter: Character):
        mana_before = fighter.current_mana
        actual = fighter.drain_mana(10)
        assert actual == 10
        assert fighter.current_mana == mana_before - 10

    def test_drain_mana_clamps_to_available(self, fighter: Character):
        fighter.spend_mana(fighter.current_mana - 5)
        actual = fighter.drain_mana(20)
        assert actual == 5
        assert fighter.current_mana == 0

    def test_drain_mana_returns_zero_when_empty(self, fighter: Character):
        fighter.drain_mana(fighter.current_mana)
        actual = fighter.drain_mana(10)
        assert actual == 0
        assert fighter.current_mana == 0


class TestCharacterPosition:
    def test_change_position_to_back(self, fighter: Character):
        fighter.change_position(Position.BACK)
        assert fighter.position == Position.BACK

    def test_change_position_to_front(self, fighter: Character):
        fighter.change_position(Position.BACK)
        fighter.change_position(Position.FRONT)
        assert fighter.position == Position.FRONT


class TestCharacterApplyRegen:
    def test_apply_regen_restores_hp(self, fighter: Character):
        fighter.take_damage(100)
        fighter.apply_regen()
        # apply_regen calls heal(hp_regen), CON bonus applied inside heal
        con = 5
        expected_heal = int(fighter.hp_regen * (1 + con * CON_HEAL_BONUS_PER_POINT))
        assert fighter.current_hp == fighter.max_hp - 100 + expected_heal

    def test_apply_regen_restores_mana(self, fighter: Character):
        fighter.spend_mana(100)
        fighter.apply_regen()
        assert fighter.current_mana == fighter.max_mana - 100 + fighter.mana_regen

    def test_apply_regen_does_not_exceed_max(self, fighter: Character):
        fighter.take_damage(1)
        fighter.apply_regen()
        assert fighter.current_hp == fighter.max_hp


class TestCharacterThresholdBonuses:
    def test_no_threshold_bonus_with_low_stats(self, fighter: Character):
        bonuses = fighter.get_threshold_bonuses()
        assert bonuses.get(BONUS_ATK_PHYSICAL, 0) == 0

    def test_strength_threshold_bonus_at_18(self, threshold_calc):
        attrs = Attributes({
            AttributeType.STRENGTH: 18,
            AttributeType.DEXTERITY: 8,
            AttributeType.CONSTITUTION: 5,
            AttributeType.INTELLIGENCE: 3,
            AttributeType.WISDOM: 4,
            AttributeType.CHARISMA: 3,
            AttributeType.MIND: 4,
        })
        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
        )
        char = Character(name="Strong", attributes=attrs, config=config)
        bonuses = char.get_threshold_bonuses()
        assert bonuses[BONUS_ATK_PHYSICAL] == 2
        assert bonuses[BONUS_DEF_PHYSICAL] == 1
        assert bonuses[BONUS_HP] == 2

    def test_threshold_bonus_affects_physical_defense(self, threshold_calc):
        attrs = Attributes({
            AttributeType.STRENGTH: 18,
            AttributeType.DEXTERITY: 8,
            AttributeType.CONSTITUTION: 5,
            AttributeType.INTELLIGENCE: 3,
            AttributeType.WISDOM: 4,
            AttributeType.CHARISMA: 3,
            AttributeType.MIND: 4,
        })
        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
        )
        char = Character(name="Strong", attributes=attrs, config=config)
        # def_physical base: (8+5+18) * 5 = 155
        # threshold bonus: +1 def_physical_mod
        # total: (8+5+18) * (5+1) = 186
        assert char.physical_defense == 186

    def test_multiple_attributes_stack_bonuses(self, threshold_calc):
        attrs = Attributes({
            AttributeType.STRENGTH: 18,
            AttributeType.DEXTERITY: 18,
            AttributeType.CONSTITUTION: 18,
            AttributeType.INTELLIGENCE: 3,
            AttributeType.WISDOM: 4,
            AttributeType.CHARISMA: 3,
            AttributeType.MIND: 4,
        })
        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
        )
        char = Character(name="Tank", attributes=attrs, config=config)
        bonuses = char.get_threshold_bonuses()
        # STR 18: def_physical_mod +1
        # DEX 18: def_physical_mod +1
        # CON 18: def_physical_mod +1
        assert bonuses[BONUS_DEF_PHYSICAL] == 3


class TestCharacterDependencyInjection:
    def test_accepts_injected_effect_manager(
        self, fighter_attrs, threshold_calc,
    ):
        custom_manager = EffectManager()
        config = CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=threshold_calc,
            effect_manager=custom_manager,
        )
        char = Character(name="Injected", attributes=fighter_attrs, config=config)
        assert char.effect_manager is custom_manager


class TestCharacterAddEffect:

    def test_add_effect_via_manager(self, fighter: Character) -> None:
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 5, 3)
        fighter.effect_manager.add_effect(buff)
        assert fighter.effect_manager.count == 1

    def test_no_active_effects_by_default(self, fighter: Character) -> None:
        assert fighter.effect_manager.count == 0

    def test_has_active_effects_after_add(self, fighter: Character) -> None:
        buff = create_flat_buff(ModifiableStat.SPEED, 5, 3)
        fighter.effect_manager.add_effect(buff)
        assert fighter.effect_manager.count > 0


class TestCharacterThresholdCacheInvalidation:

    def test_invalidate_threshold_cache(self, fighter: Character) -> None:
        bonuses_before = fighter.get_threshold_bonuses()
        fighter.invalidate_threshold_cache()
        bonuses_after = fighter.get_threshold_bonuses()
        assert bonuses_before == bonuses_after
