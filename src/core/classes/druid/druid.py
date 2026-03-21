from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.core.classes.druid.animal_form import (
    AnimalForm,
    AnimalFormModifier,
    load_animal_form_modifiers,
)
from src.core.classes.druid.druid_config import load_druid_config
from src.core.classes.druid.field_condition import (
    FieldConditionConfig,
    FieldConditionType,
    load_field_condition_configs,
)

_CONFIG = load_druid_config()
_FORM_MODIFIERS = load_animal_form_modifiers()
_FIELD_CONFIGS = load_field_condition_configs()


class Druid(Character):
    """Druida: Controle/Transformacao com formas animais e campo."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._current_form = AnimalForm.HUMANOID
        self._active_field: FieldConditionType | None = None
        self._field_remaining_turns: int = 0

    # --- Properties ---

    @property
    def current_form(self) -> AnimalForm:
        return self._current_form

    @property
    def active_field(self) -> FieldConditionType | None:
        return self._active_field

    @property
    def field_remaining_turns(self) -> int:
        return self._field_remaining_turns

    @property
    def active_field_config(self) -> FieldConditionConfig | None:
        """Config da condicao de campo ativa (None se nenhuma)."""
        if self._active_field is None:
            return None
        return _FIELD_CONFIGS[self._active_field]

    # --- ShapeShift ---

    def transform(self, form: AnimalForm) -> bool:
        """Transforma em forma animal. Custa mana. Retorna False se falhar."""
        if form == self._current_form:
            return False
        if not self.spend_mana(_CONFIG.transform_mana_cost):
            return False
        self._current_form = form
        return True

    def revert_form(self) -> None:
        """Reverte para HUMANOID. Gratis."""
        self._current_form = AnimalForm.HUMANOID

    # --- Field Conditions ---

    def create_field_condition(self, condition: FieldConditionType) -> bool:
        """Cria condicao de campo. Custa mana. Substitui anterior."""
        if not self.spend_mana(_CONFIG.field_mana_cost):
            return False
        self._active_field = condition
        self._field_remaining_turns = _FIELD_CONFIGS[condition].default_duration
        return True

    def clear_field_condition(self) -> None:
        """Remove condicao de campo ativa."""
        self._active_field = None
        self._field_remaining_turns = 0

    def tick_field_condition(self) -> None:
        """Decrementa duracao do campo. Auto-clear em 0."""
        if self._active_field is None:
            return
        self._field_remaining_turns -= 1
        if self._field_remaining_turns <= 0:
            self.clear_field_condition()

    # --- Stat Overrides ---

    @property
    def physical_attack(self) -> int:
        base = super().physical_attack
        return int(base * self._form_mod.phys_atk_multiplier)

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        nature = 1.0 + _CONFIG.nature_atk_bonus
        return int(base * self._form_mod.mag_atk_multiplier * nature)

    @property
    def physical_defense(self) -> int:
        base = super().physical_defense
        return int(base * self._form_mod.phys_def_multiplier)

    @property
    def magical_defense(self) -> int:
        base = super().magical_defense
        return int(base * self._form_mod.mag_def_multiplier)

    @property
    def speed(self) -> int:
        base = super().speed
        return int(base * self._form_mod.speed_multiplier)

    @property
    def hp_regen(self) -> int:
        base = super().hp_regen
        form_mult = self._form_mod.hp_regen_multiplier
        passive = 1.0 + _CONFIG.hp_regen_bonus
        return int(base * form_mult * passive)

    @property
    def mana_regen(self) -> int:
        base = super().mana_regen
        return int(base * (1.0 + _CONFIG.mana_regen_bonus))

    # --- Healing Override ---

    def heal(self, amount: int) -> int:
        """Cura aprimorada: +healing_bonus ao amount."""
        enhanced = int(amount * (1.0 + _CONFIG.healing_bonus))
        return super().heal(enhanced)

    # --- Helpers ---

    @property
    def _form_mod(self) -> AnimalFormModifier:
        return _FORM_MODIFIERS[self._current_form]

    def get_resource_snapshots(self) -> tuple[ClassResourceSnapshot, ...]:
        """Retorna snapshots dos recursos do Druid para a UI."""
        return (
            ClassResourceSnapshot(
                name="Form",
                display_type=ResourceDisplayType.TOGGLE,
                current=1,
                maximum=1,
                color=(109, 139, 34),
                label=self._current_form.name,
            ),
        )
