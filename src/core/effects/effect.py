"""Effect ABC - base para todos os efeitos temporarios."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.effects.effect_category import EffectCategory
from src.core.effects.stat_modifier import StatModifier
from src.core.effects.tick_result import TickResult

PERMANENT_DURATION = -1


class Effect(ABC):
    """Base para buffs, debuffs, DoTs, CC e outros efeitos temporarios.

    Lifecycle (Template Method):
        on_apply() -> tick() cada turno -> on_expire()

    tick() chama _do_tick() (hook) + _decrement_duration().
    Subclasses implementam name e stacking_key (abstract properties).
    Subclasses overridam _do_tick(), on_apply(), on_expire(), get_modifiers().
    """

    def __init__(self, duration: int) -> None:
        self._duration = duration
        self._remaining_turns = duration
        self._expired = False
        self._expire_handled = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome legivel para display e logging."""
        ...

    @property
    @abstractmethod
    def stacking_key(self) -> str:
        """Chave para regras de stacking no EffectManager."""
        ...

    @property
    @abstractmethod
    def category(self) -> EffectCategory:
        """Categoria do efeito (BUFF, DEBUFF, AILMENT)."""
        ...

    @property
    def duration(self) -> int:
        """Duracao original em turnos."""
        return self._duration

    @property
    def remaining_turns(self) -> int:
        """Turnos restantes. -1 = permanente."""
        return self._remaining_turns

    @property
    def is_expired(self) -> bool:
        """True se o efeito expirou ou foi forcado a expirar."""
        return self._expired

    def on_apply(self) -> None:
        """Hook chamado uma vez quando o efeito e aplicado."""

    def tick(self) -> TickResult:
        """Chamado uma vez por turno. Retorna resultado do tick."""
        if self._expired:
            return TickResult()
        result = self._do_tick()
        self._decrement_duration()
        return result

    def on_expire(self) -> None:
        """Hook chamado quando o efeito expira ou e removido."""

    def expire_safely(self) -> None:
        """Chama on_expire() no maximo uma vez. Idempotente."""
        if self._expire_handled:
            return
        self._expire_handled = True
        self.on_expire()

    def force_expire(self) -> None:
        """Marca como expirado (ex: cleanse, dispel)."""
        self._expired = True

    def refresh_duration(self, new_duration: int) -> None:
        """Reseta turnos restantes para nova duracao."""
        self._remaining_turns = new_duration
        self._expired = False
        self._expire_handled = False

    def _do_tick(self) -> TickResult:
        """Hook para logica de tick. Override para DoTs, HoTs, etc."""
        return TickResult()

    def get_modifiers(self) -> list[StatModifier]:
        """Modificadores de stat ativos. Override para buffs/debuffs."""
        return []

    def _decrement_duration(self) -> None:
        """Decrementa duracao. Marca expirado quando chega a zero."""
        if self._remaining_turns == PERMANENT_DURATION:
            return
        self._remaining_turns -= 1
        if self._remaining_turns <= 0:
            self._expired = True
