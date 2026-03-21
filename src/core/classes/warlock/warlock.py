from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.core.classes.warlock.familiar import (
    FamiliarType,
    load_familiar_configs,
)
from src.core.classes.warlock.insanity_bar import InsanityBar
from src.core.classes.warlock.insatiable_thirst import InsatiableThirst
from src.core.classes.warlock.warlock_config import load_warlock_config

_CONFIG = load_warlock_config()
_FAMILIAR_CONFIGS = load_familiar_configs()


class Warlock(Character):
    """Bruxo: Debuffer/DPS com Insanidade, Sede Insaciavel e Familiares."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
        familiar: FamiliarType = FamiliarType.IMP,
    ) -> None:
        super().__init__(name, attributes, config)
        self._insanity = InsanityBar()
        self._thirst = InsatiableThirst()
        self._familiar = familiar
        self._spell_ramp_active = False

    @property
    def insanity(self) -> InsanityBar:
        return self._insanity

    @property
    def thirst(self) -> InsatiableThirst:
        return self._thirst

    @property
    def familiar(self) -> FamiliarType:
        return self._familiar

    def set_familiar(self, familiar: FamiliarType) -> None:
        self._familiar = familiar

    # --- Insanity ---

    def take_damage(self, amount: int) -> int:
        """Recebe dano e ganha insanidade proporcional."""
        actual = super().take_damage(amount)
        insanity_gain = int(actual * _CONFIG.insanity_on_damage_ratio)
        self._insanity.gain(insanity_gain)
        return actual

    def generate_insanity_from_cast(self) -> int:
        """Gera insanidade ao usar habilidade."""
        return self._insanity.gain(_CONFIG.insanity_on_cast)

    def decay_insanity(self) -> int:
        """Decai insanidade no fim do turno."""
        return self._insanity.decay(_CONFIG.insanity_decay_per_turn)

    # --- Stats com insanity + familiar + thirst ---

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        insanity_mult = 1.0 + (
            self._insanity.ratio * _CONFIG.insanity_atk_bonus_at_max
        )
        thirst_mult = self._thirst_atk_multiplier
        familiar_mult = self._familiar_bonus("magical_attack")
        return int(base * insanity_mult * thirst_mult * familiar_mult)

    @property
    def magical_defense(self) -> int:
        base = super().magical_defense
        insanity_penalty = 1.0 - (
            self._insanity.ratio * _CONFIG.insanity_def_penalty_at_max
        )
        familiar_mult = self._familiar_bonus("magical_defense")
        return int(base * insanity_penalty * familiar_mult)

    @property
    def hp_regen(self) -> int:
        base = super().hp_regen
        if self._thirst.is_active:
            return int(base * (1.0 + _CONFIG.thirst_regen_bonus))
        return base

    @property
    def physical_defense(self) -> int:
        base = super().physical_defense
        if self._thirst.is_active:
            return int(base * (1.0 + _CONFIG.thirst_def_bonus))
        return base

    @property
    def speed(self) -> int:
        base = super().speed
        familiar_mult = self._familiar_bonus("speed")
        return int(base * familiar_mult)

    # --- Insatiable Thirst ---

    def check_thirst(self) -> bool:
        """Checa HP e acumula sede. Retorna True se trigger."""
        hp_ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 1.0
        triggered = self._thirst.check_and_stack(hp_ratio)
        if triggered:
            con = self._attributes.get(AttributeType.CONSTITUTION)
            self._thirst.activate(duration=con)
        return triggered

    def tick_thirst(self) -> None:
        """Decrementa duracao da sede insaciavel."""
        self._thirst.tick()

    # --- Passivas ---

    def on_inflict_bleed(self, damage: int) -> int:
        """Recupera HP ao infligir bleed. Retorna HP restaurado."""
        heal_amount = int(damage * _CONFIG.life_drain_ratio)
        return self.heal(heal_amount)

    def register_cast(self) -> None:
        """Registra uso de habilidade. Proxima skill tera bonus."""
        self._spell_ramp_active = True
        self.generate_insanity_from_cast()

    @property
    def spell_damage_bonus(self) -> float:
        """Bonus de dano da proxima skill (0.0 se inativo)."""
        if not self._spell_ramp_active:
            return 0.0
        cha = self._attributes.get(AttributeType.CHARISMA)
        return _CONFIG.spell_ramp_bonus + (cha * _CONFIG.spell_ramp_cha_scaling)

    def consume_spell_ramp(self) -> float:
        """Consome bonus de spell ramp. Retorna bonus e reseta."""
        bonus = self.spell_damage_bonus
        self._spell_ramp_active = False
        return bonus

    # --- Helpers ---

    @property
    def _thirst_atk_multiplier(self) -> float:
        if self._thirst.is_active:
            return 1.0 + _CONFIG.thirst_atk_bonus
        return 1.0

    def _familiar_bonus(self, stat_name: str) -> float:
        """Retorna multiplicador do familiar para o stat dado."""
        fam_config = _FAMILIAR_CONFIGS[self._familiar]
        if fam_config.stat_bonus_type == stat_name:
            return 1.0 + fam_config.stat_bonus_pct
        return 1.0

    def get_resource_snapshots(self) -> tuple[ClassResourceSnapshot, ...]:
        """Retorna snapshots dos recursos do Warlock para a UI."""
        return (
            ClassResourceSnapshot(
                name="Insanity",
                display_type=ResourceDisplayType.BAR,
                current=self.insanity.current,
                maximum=InsanityBar.MAX_INSANITY,
                color=(180, 50, 200),
            ),
        )
