"""EffectManager - gerencia efeitos ativos num alvo."""

from __future__ import annotations

from src.core.effects.effect import Effect
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stacking import StackingPolicy
from src.core.effects.stacking_resolver import StackingResolver
from src.core.effects.stat_modifier import StatModifier
from src.core.effects.tick_result import TickResult


class EffectManager:
    """Gerencia efeitos ativos num alvo (composicao standalone).

    Responsabilidades:
        - Adicionar/remover efeitos com regras de stacking
        - Tickar todos os efeitos por turno
        - Agregar modificadores de stats dos efeitos ativos
        - Consultar efeitos ativos por chave
    """

    def __init__(self) -> None:
        self._effects: list[Effect] = []
        self._stacking = StackingResolver()

    @property
    def active_effects(self) -> list[Effect]:
        """Lista de efeitos ativos (nao-expirados)."""
        return [e for e in self._effects if not e.is_expired]

    @property
    def count(self) -> int:
        """Quantidade de efeitos ativos."""
        return sum(1 for e in self._effects if not e.is_expired)

    def set_stacking_policy(
        self, stacking_key: str, policy: StackingPolicy,
    ) -> None:
        """Configura politica de stacking para uma chave."""
        self._stacking.set_policy(stacking_key, policy)

    def add_effect(self, effect: Effect) -> None:
        """Adiciona efeito aplicando regras de stacking."""
        self._stacking.resolve_add(self._effects, effect)

    def remove_effect(self, effect: Effect) -> None:
        """Remove efeito especifico. Chama force_expire + on_expire."""
        if effect not in self._effects:
            return
        effect.force_expire()
        effect.expire_safely()
        self._effects.remove(effect)

    def remove_by_key(self, stacking_key: str) -> int:
        """Remove todos os efeitos com a chave. Retorna qtd removida."""
        to_remove = _find_active_by_key(self._effects, stacking_key)
        for effect in to_remove:
            self.remove_effect(effect)
        return len(to_remove)

    def tick_all(self) -> list[TickResult]:
        """Ticka todos os efeitos. Auto-expire os que acabaram."""
        results = [e.tick() for e in list(self._effects)]
        _cleanup_expired(self._effects)
        return results

    def get_modifiers_for(self, stat: ModifiableStat) -> list[StatModifier]:
        """Todos os modificadores ativos para um stat especifico."""
        return [
            mod for e in self.active_effects
            for mod in e.get_modifiers() if mod.stat == stat
        ]

    def aggregate_modifier(self, stat: ModifiableStat) -> StatModifier:
        """Agrega modificadores de um stat: soma flat + soma percent."""
        modifiers = self.get_modifiers_for(stat)
        total_flat = sum(m.flat for m in modifiers)
        total_percent = sum(m.percent for m in modifiers)
        return StatModifier(stat=stat, flat=total_flat, percent=total_percent)

    def has_effect(self, stacking_key: str) -> bool:
        """True se algum efeito ativo com essa chave existe."""
        return any(
            e.stacking_key == stacking_key for e in self.active_effects
        )

    def clear_all(self) -> None:
        """Remove todos os efeitos, chamando on_expire em cada um."""
        for effect in list(self._effects):
            effect.force_expire()
            effect.expire_safely()
        self._effects.clear()


def _find_active_by_key(
    effects: list[Effect], stacking_key: str,
) -> list[Effect]:
    return [
        e for e in effects
        if e.stacking_key == stacking_key and not e.is_expired
    ]


def _cleanup_expired(effects: list[Effect]) -> None:
    expired = [e for e in effects if e.is_expired]
    for effect in expired:
        effect.expire_safely()
        effects.remove(effect)
