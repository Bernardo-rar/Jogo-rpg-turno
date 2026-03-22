from unittest.mock import PropertyMock, patch

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.barbarian.barbarian import Barbarian
from src.core.classes.barbarian.fury_bar import FuryBar

# Barbarian stats: STR=12, DEX=6, CON=10, INT=3, WIS=4, CHA=5, MIND=4
# Modifiers from barbarian.json: hit_dice=12, mod_hp_flat=2, mod_hp_mult=12,
#   mod_atk_physical=12, mod_atk_magical=2, mod_def_physical=5, mod_def_magical=3
# base physical_attack = (0 + 12 + 6) * 12 = 216 (weapon_die=0, STR=12, DEX=6)
# base physical_defense = (6 + 10 + 12) * 5 = 140
# base magical_attack = (0 + 4 + 3) * 2 = 14
# base magical_defense = (10 + 4 + 3) * 3 = 51

BARBARIAN_MODIFIERS = ClassModifiers.from_json("data/classes/barbarian.json")
EMPTY_THRESHOLDS = ThresholdCalculator({})
BARBARIAN_CONFIG = CharacterConfig(
    class_modifiers=BARBARIAN_MODIFIERS,
    threshold_calculator=EMPTY_THRESHOLDS,
)


def _barbarian_attrs() -> Attributes:
    attrs = Attributes()
    attrs.set(AttributeType.STRENGTH, 12)
    attrs.set(AttributeType.DEXTERITY, 6)
    attrs.set(AttributeType.CONSTITUTION, 10)
    attrs.set(AttributeType.INTELLIGENCE, 3)
    attrs.set(AttributeType.WISDOM, 4)
    attrs.set(AttributeType.CHARISMA, 5)
    attrs.set(AttributeType.MIND, 4)
    return attrs


@pytest.fixture
def barbarian() -> Barbarian:
    return Barbarian(
        "Ragnar",
        _barbarian_attrs(),
        BARBARIAN_CONFIG,
    )


class TestBarbarianIsCharacter:
    """LSP: Barbarian deve funcionar como Character em qualquer contexto."""

    def test_is_instance_of_character(self, barbarian: Barbarian):
        assert isinstance(barbarian, Character)

    def test_has_name(self, barbarian: Barbarian):
        assert barbarian.name == "Ragnar"

    def test_has_hp(self, barbarian: Barbarian):
        assert barbarian.max_hp > 0

    def test_take_damage_works(self, barbarian: Barbarian):
        original = barbarian.current_hp
        barbarian.take_damage(10)
        assert barbarian.current_hp == original - 10

    def test_heal_works(self, barbarian: Barbarian):
        barbarian.take_damage(20)
        barbarian.heal(10)
        # CON=10, heal(10) -> int(10 * 1.5) = 15
        assert barbarian.current_hp == barbarian.max_hp - 20 + 15

    def test_is_alive(self, barbarian: Barbarian):
        assert barbarian.is_alive is True

    def test_speed(self, barbarian: Barbarian):
        assert barbarian.speed == 6  # DEX


class TestBarbarianPosition:
    def test_default_position_is_front(self, barbarian: Barbarian):
        assert barbarian.position == Position.FRONT

    def test_can_change_position(self, barbarian: Barbarian):
        barbarian.change_position(Position.BACK)
        assert barbarian.position == Position.BACK


class TestBarbarianBaseStats:
    def test_physical_attack_no_fury_no_damage(self, barbarian: Barbarian):
        assert barbarian.physical_attack == 216

    def test_physical_defense(self, barbarian: Barbarian):
        assert barbarian.physical_defense == 140

    def test_magical_attack(self, barbarian: Barbarian):
        assert barbarian.magical_attack == 14

    def test_magical_defense(self, barbarian: Barbarian):
        assert barbarian.magical_defense == 51


class TestBarbarianFuryBar:
    def test_has_fury_bar(self, barbarian: Barbarian):
        assert isinstance(barbarian.fury_bar, FuryBar)

    def test_fury_starts_at_zero(self, barbarian: Barbarian):
        assert barbarian.fury_bar.current == 0

    def test_fury_max_based_on_max_hp(self, barbarian: Barbarian):
        # max_hp * fury_max_ratio (0.25)
        expected = int(barbarian.max_hp * 0.25)
        assert barbarian.fury_bar.max_fury == expected


class TestBarbarianFuryOnDamage:
    def test_taking_damage_generates_fury(self, barbarian: Barbarian):
        barbarian.take_damage(100)
        # 100 * 0.10 = 10 fury
        assert barbarian.fury_bar.current == 10

    def test_fury_gain_capped_at_max(self, barbarian: Barbarian):
        max_fury = barbarian.fury_bar.max_fury
        # Preencher fury diretamente e verificar que dano extra nao ultrapassa
        barbarian.fury_bar.gain(max_fury)
        barbarian.take_damage(100)
        assert barbarian.fury_bar.current == max_fury

    def test_lethal_damage_generates_fury(self, barbarian: Barbarian):
        hp = barbarian.current_hp
        barbarian.take_damage(hp)
        # Dano letal gera fury antes de morrer
        expected = int(hp * 0.10)
        assert barbarian.fury_bar.current == min(
            expected, barbarian.fury_bar.max_fury,
        )


class TestBarbarianFuryFromAttack:
    def test_generate_fury_from_attack(self, barbarian: Barbarian):
        barbarian.generate_fury_from_attack()
        # fury_on_basic_attack = 5
        assert barbarian.fury_bar.current == 5

    def test_multiple_attacks_accumulate(self, barbarian: Barbarian):
        barbarian.generate_fury_from_attack()
        barbarian.generate_fury_from_attack()
        assert barbarian.fury_bar.current == 10


class TestBarbarianFuryDecay:
    def test_decay_fury_reduces(self, barbarian: Barbarian):
        barbarian.take_damage(100)  # ganha 10 fury
        barbarian.decay_fury()
        # fury_decay_per_turn = 3
        assert barbarian.fury_bar.current == 7


class TestBarbarianFuryAttackBonus:
    def test_fury_increases_physical_attack(self, barbarian: Barbarian):
        base_atk = barbarian.physical_attack
        # Encher fury ao maximo
        barbarian.fury_bar.gain(barbarian.fury_bar.max_fury)
        boosted = barbarian.physical_attack
        # 216 * (1.0 + 1.0 * 0.30) = 216 * 1.30 = 280.8 -> 280
        assert boosted == int(base_atk * 1.30)

    def test_half_fury_gives_half_bonus(self, barbarian: Barbarian):
        base_atk = barbarian.physical_attack
        barbarian.fury_bar.gain(barbarian.fury_bar.max_fury // 2)
        ratio = barbarian.fury_bar.fury_ratio
        expected = int(base_atk * (1.0 + ratio * 0.30))
        assert barbarian.physical_attack == expected


class TestBarbarianMissingHpRatioEdge:
    def test_missing_hp_ratio_zero_max_hp(self, barbarian: Barbarian):
        with patch.object(type(barbarian), "max_hp", new_callable=PropertyMock, return_value=0):
            assert barbarian._missing_hp_ratio == 0.0


class TestBarbarianMissingHpBonus:
    def test_full_hp_no_bonus(self, barbarian: Barbarian):
        assert barbarian.physical_attack == 216

    def test_half_hp_gives_bonus(self, barbarian: Barbarian):
        barbarian.take_damage(barbarian.max_hp // 2)
        # Reset fury to isolate missing HP bonus
        barbarian.fury_bar.spend(barbarian.fury_bar.current)
        missing_ratio = 1.0 - (barbarian.current_hp / barbarian.max_hp)
        expected = int(216 * (1.0 + missing_ratio * 0.25))
        assert barbarian.physical_attack == expected

    def test_low_hp_gives_more_bonus(self, barbarian: Barbarian):
        barbarian.take_damage(barbarian.max_hp - 1)
        barbarian.fury_bar.spend(barbarian.fury_bar.current)
        missing_ratio = 1.0 - (1 / barbarian.max_hp)
        expected = int(216 * (1.0 + missing_ratio * 0.25))
        assert barbarian.physical_attack == expected


class TestBarbarianFuryRegenBonus:
    def test_fury_increases_hp_regen(self, barbarian: Barbarian):
        base_regen = barbarian.hp_regen
        barbarian.fury_bar.gain(barbarian.fury_bar.max_fury)
        boosted = barbarian.hp_regen
        # base * (1.0 + 1.0 * 0.20) = base * 1.20
        assert boosted == int(base_regen * 1.20)


class TestBarbarianLevelUp:
    def test_level_up_updates_fury_max(self):
        config_lvl1 = CharacterConfig(
            class_modifiers=BARBARIAN_MODIFIERS,
            threshold_calculator=EMPTY_THRESHOLDS,
            level=1,
        )
        b = Barbarian("B", _barbarian_attrs(), config_lvl1)
        old_max = b.fury_bar.max_fury
        b._set_level(3)
        # max_hp muda com level, fury max deve acompanhar
        new_expected = int(b.max_hp * 0.25)
        assert b.fury_bar.max_fury == new_expected
        assert b.fury_bar.max_fury > old_max
