from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.derived_stats import (
    AttackInput,
    DefenseInput,
    HpInput,
    calculate_attack,
    calculate_defense,
    calculate_hp,
    calculate_hp_regen,
    calculate_mana,
    calculate_mana_regen,
)
from src.core.attributes.threshold_calculator import (
    BONUS_ATK_MAGICAL,
    BONUS_ATK_PHYSICAL,
    BONUS_DEF_MAGICAL,
    BONUS_DEF_PHYSICAL,
    BONUS_HP,
    BONUS_HP_REGEN,
    ThresholdCalculator,
)
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position

WEAPON_DIE_NONE = 0


class Character:
    """Classe base de personagem. Subclasses (Fighter, Mage, etc.) herdam dela."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        class_modifiers: ClassModifiers,
        *,
        threshold_calculator: ThresholdCalculator,
        level: int = 1,
        position: Position = Position.FRONT,
    ) -> None:
        self._name = name
        self._attributes = attributes
        self._modifiers = class_modifiers
        self._threshold_calc = threshold_calculator
        self._level = level
        self._position = position
        self._alive = True
        self._threshold_cache: dict[str, int] | None = None
        self._current_hp = self.max_hp
        self._current_mana = self.max_mana

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> int:
        return self._level

    @property
    def position(self) -> Position:
        return self._position

    @property
    def is_alive(self) -> bool:
        return self._alive

    @property
    def current_hp(self) -> int:
        return self._current_hp

    @property
    def current_mana(self) -> int:
        return self._current_mana

    @property
    def max_hp(self) -> int:
        con = self._attributes.get(AttributeType.CONSTITUTION)
        bonus = self.get_threshold_bonuses().get(BONUS_HP, 0)
        return calculate_hp(HpInput(
            hit_dice=self._modifiers.hit_dice,
            con=con,
            vida_mod=self._modifiers.vida_mod + bonus,
            mod_hp=self._modifiers.mod_hp,
            level=self._level,
        ))

    @property
    def max_mana(self) -> int:
        mind = self._attributes.get(AttributeType.MIND)
        return calculate_mana(
            mana_multiplier=self._modifiers.mana_multiplier,
            mind=mind,
        )

    @property
    def physical_attack(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_ATK_PHYSICAL, 0)
        return calculate_attack(AttackInput(
            weapon_die=WEAPON_DIE_NONE,
            primary_stat=self._attributes.get(AttributeType.STRENGTH),
            secondary_stat=self._attributes.get(AttributeType.DEXTERITY),
            modifier=self._modifiers.mod_atk_physical + bonus,
        ))

    @property
    def magical_attack(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_ATK_MAGICAL, 0)
        return calculate_attack(AttackInput(
            weapon_die=WEAPON_DIE_NONE,
            primary_stat=self._attributes.get(AttributeType.WISDOM),
            secondary_stat=self._attributes.get(AttributeType.INTELLIGENCE),
            modifier=self._modifiers.mod_atk_magical + bonus,
        ))

    @property
    def speed(self) -> int:
        return self._attributes.get(AttributeType.DEXTERITY)

    @property
    def physical_defense(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_DEF_PHYSICAL, 0)
        return calculate_defense(DefenseInput(
            primary_stat=self._attributes.get(AttributeType.DEXTERITY),
            secondary_stat=self._attributes.get(AttributeType.CONSTITUTION),
            tertiary_stat=self._attributes.get(AttributeType.STRENGTH),
            modifier=self._modifiers.mod_def_physical + bonus,
        ))

    @property
    def magical_defense(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_DEF_MAGICAL, 0)
        return calculate_defense(DefenseInput(
            primary_stat=self._attributes.get(AttributeType.CONSTITUTION),
            secondary_stat=self._attributes.get(AttributeType.WISDOM),
            tertiary_stat=self._attributes.get(AttributeType.INTELLIGENCE),
            modifier=self._modifiers.mod_def_magical + bonus,
        ))

    @property
    def hp_regen(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_HP_REGEN, 0)
        return calculate_hp_regen(
            constitution=self._attributes.get(AttributeType.CONSTITUTION),
            regen_hp_mod=self._modifiers.regen_hp_mod + bonus,
        )

    @property
    def mana_regen(self) -> int:
        return calculate_mana_regen(
            mind=self._attributes.get(AttributeType.MIND),
            regen_mana_mod=self._modifiers.regen_mana_mod,
        )

    def take_damage(self, amount: int) -> int:
        actual = min(amount, self._current_hp)
        self._current_hp -= actual
        if self._current_hp == 0:
            self._alive = False
        return actual

    def heal(self, amount: int) -> int:
        if not self._alive:
            return 0
        actual = min(amount, self.max_hp - self._current_hp)
        self._current_hp += actual
        return actual

    def spend_mana(self, amount: int) -> bool:
        if amount > self._current_mana:
            return False
        self._current_mana -= amount
        return True

    def restore_mana(self, amount: int) -> int:
        actual = min(amount, self.max_mana - self._current_mana)
        self._current_mana += actual
        return actual

    def change_position(self, new_position: Position) -> None:
        self._position = new_position

    def apply_regen(self) -> None:
        self.heal(self.hp_regen)
        self.restore_mana(self.mana_regen)

    def get_threshold_bonuses(self) -> dict[str, int]:
        """Agrega bonus de threshold de todos os 7 atributos (cached)."""
        if self._threshold_cache is not None:
            return self._threshold_cache
        total: dict[str, int] = {}
        for attr_type in AttributeType:
            value = self._attributes.get(attr_type)
            bonuses = self._threshold_calc.calculate_bonuses(attr_type, value)
            for key, bonus in bonuses.items():
                total[key] = total.get(key, 0) + bonus
        self._threshold_cache = total
        return total

    def invalidate_threshold_cache(self) -> None:
        """Invalida cache de threshold bonuses (chamar apos mudar atributos)."""
        self._threshold_cache = None
