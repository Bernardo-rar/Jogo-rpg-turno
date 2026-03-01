"""EffectManager - gerencia efeitos ativos num alvo."""

from __future__ import annotations

from src.core.effects.effect import Effect
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stacking import StackingPolicy
from src.core.effects.stat_modifier import StatModifier
from src.core.effects.tick_result import TickResult

DEFAULT_STACKING_POLICY = StackingPolicy.REPLACE


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
        self._stacking_policies: dict[str, StackingPolicy] = {}

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
        self._stacking_policies[stacking_key] = policy

    def add_effect(self, effect: Effect) -> None:
        """Adiciona efeito aplicando regras de stacking."""
        policy = self._get_policy(effect.stacking_key)
        self._apply_stacking(effect, policy)

    def remove_effect(self, effect: Effect) -> None:
        """Remove efeito especifico. Chama force_expire + on_expire."""
        if effect not in self._effects:
            return
        effect.force_expire()
        if not effect._expire_handled:
            effect._expire_handled = True
            effect.on_expire()
        self._effects.remove(effect)

    def remove_by_key(self, stacking_key: str) -> int:
        """Remove todos os efeitos com a chave. Retorna qtd removida."""
        to_remove = self._find_by_key(stacking_key)
        for effect in to_remove:
            self.remove_effect(effect)
        return len(to_remove)

    def tick_all(self) -> list[TickResult]:
        """Ticka todos os efeitos. Auto-expire os que acabaram."""
        results: list[TickResult] = []
        for effect in list(self._effects):
            result = effect.tick()
            results.append(result)
        self._cleanup_expired()
        return results

    def get_modifiers_for(self, stat: ModifiableStat) -> list[StatModifier]:
        """Todos os modificadores ativos para um stat especifico."""
        modifiers: list[StatModifier] = []
        for effect in self.active_effects:
            for mod in effect.get_modifiers():
                if mod.stat == stat:
                    modifiers.append(mod)
        return modifiers

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
            if not effect._expire_handled:
                effect._expire_handled = True
                effect.on_expire()
        self._effects.clear()

    def _get_policy(self, stacking_key: str) -> StackingPolicy:
        """Retorna politica configurada ou DEFAULT (REPLACE)."""
        return self._stacking_policies.get(
            stacking_key, DEFAULT_STACKING_POLICY,
        )

    def _apply_stacking(
        self, new_effect: Effect, policy: StackingPolicy,
    ) -> None:
        """Aplica regra de stacking ao adicionar efeito."""
        existing = self._find_by_key(new_effect.stacking_key)
        if not existing or policy == StackingPolicy.STACK:
            self._add_and_apply(new_effect)
            return
        if policy == StackingPolicy.REPLACE:
            self._replace_existing(existing, new_effect)
            return
        self._refresh_existing(existing[0], new_effect)

    def _find_by_key(self, stacking_key: str) -> list[Effect]:
        """Encontra efeitos ativos com a chave dada."""
        return [
            e for e in self._effects
            if e.stacking_key == stacking_key and not e.is_expired
        ]

    def _add_and_apply(self, effect: Effect) -> None:
        """Adiciona efeito e chama on_apply."""
        self._effects.append(effect)
        effect.on_apply()

    def _replace_existing(
        self, existing: list[Effect], new_effect: Effect,
    ) -> None:
        """Remove existentes e adiciona novo (REPLACE policy)."""
        for old in existing:
            old.force_expire()
            if not old._expire_handled:
                old._expire_handled = True
                old.on_expire()
            self._effects.remove(old)
        self._add_and_apply(new_effect)

    def _refresh_existing(
        self, existing: Effect, new_effect: Effect,
    ) -> None:
        """Reseta duracao do existente (REFRESH policy)."""
        existing.refresh_duration(new_effect.duration)

    def _cleanup_expired(self) -> None:
        """Remove efeitos expirados, chamando on_expire uma unica vez."""
        expired = [e for e in self._effects if e.is_expired]
        for effect in expired:
            if not effect._expire_handled:
                effect._expire_handled = True
                effect.on_expire()
            self._effects.remove(effect)
