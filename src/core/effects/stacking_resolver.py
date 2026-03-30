"""StackingResolver — encapsulates stacking policy logic for effects."""

from __future__ import annotations

from src.core.effects.effect import Effect
from src.core.effects.stacking import StackingPolicy

DEFAULT_STACKING_POLICY = StackingPolicy.REPLACE


class StackingResolver:
    """Resolves stacking behavior when adding effects."""

    def __init__(self) -> None:
        self._policies: dict[str, StackingPolicy] = {}

    def set_policy(
        self, stacking_key: str, policy: StackingPolicy,
    ) -> None:
        """Configura politica de stacking para uma chave."""
        self._policies[stacking_key] = policy

    def resolve_add(
        self, effects: list[Effect], new_effect: Effect,
    ) -> None:
        """Adds effect to list applying stacking rules."""
        policy = self._get_policy(new_effect.stacking_key)
        existing = _find_by_key(effects, new_effect.stacking_key)
        if not existing or policy == StackingPolicy.STACK:
            _add_and_apply(effects, new_effect)
            return
        if policy == StackingPolicy.REPLACE:
            _replace_existing(effects, existing, new_effect)
            return
        _refresh_existing(existing[0], new_effect)

    def _get_policy(self, stacking_key: str) -> StackingPolicy:
        return self._policies.get(
            stacking_key, DEFAULT_STACKING_POLICY,
        )


def _find_by_key(
    effects: list[Effect], stacking_key: str,
) -> list[Effect]:
    return [
        e for e in effects
        if e.stacking_key == stacking_key and not e.is_expired
    ]


def _add_and_apply(effects: list[Effect], effect: Effect) -> None:
    effects.append(effect)
    effect.on_apply()


def _replace_existing(
    effects: list[Effect],
    existing: list[Effect],
    new_effect: Effect,
) -> None:
    for old in existing:
        old.force_expire()
        old.expire_safely()
        effects.remove(old)
    _add_and_apply(effects, new_effect)


def _refresh_existing(existing: Effect, new_effect: Effect) -> None:
    existing.refresh_duration(new_effect.duration)
