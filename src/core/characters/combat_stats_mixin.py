"""Mixin para calculo de derived combat stats."""

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
)
from typing import TYPE_CHECKING

from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.damage import DamageType
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat

if TYPE_CHECKING:
    from src.core.items.weapon import Weapon

WEAPON_DIE_NONE = 0


class CombatStatsMixin:
    """Calcula derived stats (HP, mana, ataque, defesa, regen) com modifiers."""

    _attributes: Attributes
    _modifiers: ClassModifiers
    _level: int
    _effect_manager: EffectManager
    _weapon: Weapon | None

    def _apply_effect_modifiers(self, stat: ModifiableStat, base: int) -> int:
        mod = self._effect_manager.aggregate_modifier(stat)
        return mod.apply(base)

    def _get_weapon_die(self, damage_type: DamageType) -> int:
        """Retorna weapon_die se arma equipada e damage_type compativel."""
        if self._weapon is None:
            return WEAPON_DIE_NONE
        if self._weapon.damage_type != damage_type:
            return WEAPON_DIE_NONE
        return self._weapon.weapon_die

    @property
    def weapon(self) -> Weapon | None:
        return self._weapon

    def equip_weapon(self, weapon: Weapon) -> None:
        self._weapon = weapon

    def unequip_weapon(self) -> Weapon | None:
        old = self._weapon
        self._weapon = None
        return old

    @property
    def max_hp(self) -> int:
        con = self._attributes.get(AttributeType.CONSTITUTION)
        bonus = self.get_threshold_bonuses().get(BONUS_HP, 0)
        base = calculate_hp(HpInput(
            hit_dice=self._modifiers.hit_dice,
            con=con,
            vida_mod=self._modifiers.vida_mod + bonus,
            mod_hp=self._modifiers.mod_hp,
            level=self._level,
        ))
        return self._apply_effect_modifiers(ModifiableStat.MAX_HP, base)

    @property
    def max_mana(self) -> int:
        mind = self._attributes.get(AttributeType.MIND)
        base = calculate_mana(
            mana_multiplier=self._modifiers.mana_multiplier,
            mind=mind,
        )
        return self._apply_effect_modifiers(ModifiableStat.MAX_MANA, base)

    @property
    def physical_attack(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_ATK_PHYSICAL, 0)
        base = calculate_attack(AttackInput(
            weapon_die=self._get_weapon_die(DamageType.PHYSICAL),
            primary_stat=self._attributes.get(AttributeType.STRENGTH),
            secondary_stat=self._attributes.get(AttributeType.DEXTERITY),
            modifier=self._modifiers.mod_atk_physical + bonus,
        ))
        return self._apply_effect_modifiers(ModifiableStat.PHYSICAL_ATTACK, base)

    @property
    def magical_attack(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_ATK_MAGICAL, 0)
        base = calculate_attack(AttackInput(
            weapon_die=self._get_weapon_die(DamageType.MAGICAL),
            primary_stat=self._attributes.get(AttributeType.WISDOM),
            secondary_stat=self._attributes.get(AttributeType.INTELLIGENCE),
            modifier=self._modifiers.mod_atk_magical + bonus,
        ))
        return self._apply_effect_modifiers(ModifiableStat.MAGICAL_ATTACK, base)

    @property
    def speed(self) -> int:
        base = self._attributes.get(AttributeType.DEXTERITY)
        return self._apply_effect_modifiers(ModifiableStat.SPEED, base)

    @property
    def physical_defense(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_DEF_PHYSICAL, 0)
        base = calculate_defense(DefenseInput(
            primary_stat=self._attributes.get(AttributeType.DEXTERITY),
            secondary_stat=self._attributes.get(AttributeType.CONSTITUTION),
            tertiary_stat=self._attributes.get(AttributeType.STRENGTH),
            modifier=self._modifiers.mod_def_physical + bonus,
        ))
        return self._apply_effect_modifiers(ModifiableStat.PHYSICAL_DEFENSE, base)

    @property
    def magical_defense(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_DEF_MAGICAL, 0)
        base = calculate_defense(DefenseInput(
            primary_stat=self._attributes.get(AttributeType.CONSTITUTION),
            secondary_stat=self._attributes.get(AttributeType.WISDOM),
            tertiary_stat=self._attributes.get(AttributeType.INTELLIGENCE),
            modifier=self._modifiers.mod_def_magical + bonus,
        ))
        return self._apply_effect_modifiers(ModifiableStat.MAGICAL_DEFENSE, base)

    @property
    def proficiency_bonus(self) -> int:
        return self._level

    @property
    def hp_regen(self) -> int:
        bonus = self.get_threshold_bonuses().get(BONUS_HP_REGEN, 0)
        base = calculate_hp_regen(
            constitution=self._attributes.get(AttributeType.CONSTITUTION),
            regen_hp_mod=self._modifiers.regen_hp_mod + bonus,
            level=self._level,
        )
        return self._apply_effect_modifiers(ModifiableStat.HP_REGEN, base)

    @property
    def mana_regen(self) -> int:
        base = calculate_mana_regen(
            mind=self._attributes.get(AttributeType.MIND),
            regen_mana_mod=self._modifiers.regen_mana_mod,
            level=self._level,
        )
        return self._apply_effect_modifiers(ModifiableStat.MANA_REGEN, base)
