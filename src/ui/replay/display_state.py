"""Estado mutavel de HP/mana para a UI. Aplica deltas por evento."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.combat.effect_phase import EffectLogEntry
from src.ui.replay.battle_snapshot import CharacterSnapshot, RoundSnapshot

DAMAGE_KEYWORD = "damage"
HEAL_KEYWORD = "heal"


@dataclass
class _CharState:
    """Estado mutavel interno de um personagem."""

    name: str
    current_hp: int
    max_hp: int
    current_mana: int
    max_mana: int
    position: object
    is_alive: bool
    active_effects: tuple[str, ...]
    is_party: bool


class DisplayState:
    """Acumulador mutavel de HP/mana que a UI atualiza por evento."""

    def __init__(self, initial: RoundSnapshot) -> None:
        self._chars: dict[str, _CharState] = {}
        self.sync_from_snapshot(initial)

    def apply_damage(self, target_name: str, amount: int) -> None:
        char = self._chars.get(target_name)
        if char is None:
            return
        char.current_hp = max(0, char.current_hp - amount)
        char.is_alive = char.current_hp > 0

    def apply_heal(self, target_name: str, amount: int) -> None:
        char = self._chars.get(target_name)
        if char is None:
            return
        char.current_hp = min(char.max_hp, char.current_hp + amount)

    def apply_mana_restore(self, target_name: str, amount: int) -> None:
        char = self._chars.get(target_name)
        if char is None:
            return
        char.current_mana = min(char.max_mana, char.current_mana + amount)

    def apply_add_effect(self, target_name: str, effect_name: str) -> None:
        char = self._chars.get(target_name)
        if char is None:
            return
        char.active_effects = char.active_effects + (effect_name,)

    def apply_remove_effects(self, target_name: str) -> None:
        char = self._chars.get(target_name)
        if char is None:
            return
        char.active_effects = ()

    def apply_effect_ticks(self, entries: list[EffectLogEntry]) -> None:
        for entry in entries:
            if entry.is_skip or entry.value == 0:
                continue
            if DAMAGE_KEYWORD in entry.message:
                self.apply_damage(entry.character_name, entry.value)
            elif HEAL_KEYWORD in entry.message:
                self.apply_heal(entry.character_name, entry.value)

    def sync_from_snapshot(self, snapshot: RoundSnapshot) -> None:
        self._chars.clear()
        for c in snapshot.characters:
            self._chars[c.name] = _char_from_snapshot(c)

    def get_alive_map(self) -> dict[str, bool]:
        """Retorna mapa nome -> is_alive."""
        return {name: s.is_alive for name, s in self._chars.items()}

    def to_round_snapshot(self, round_number: int) -> RoundSnapshot:
        chars = tuple(_to_frozen(s) for s in self._chars.values())
        return RoundSnapshot(round_number=round_number, characters=chars)


def _char_from_snapshot(c: CharacterSnapshot) -> _CharState:
    return _CharState(
        name=c.name,
        current_hp=c.current_hp,
        max_hp=c.max_hp,
        current_mana=c.current_mana,
        max_mana=c.max_mana,
        position=c.position,
        is_alive=c.is_alive,
        active_effects=c.active_effects,
        is_party=c.is_party,
    )


def _to_frozen(s: _CharState) -> CharacterSnapshot:
    return CharacterSnapshot(
        name=s.name,
        current_hp=s.current_hp,
        max_hp=s.max_hp,
        current_mana=s.current_mana,
        max_mana=s.max_mana,
        position=s.position,
        is_alive=s.is_alive,
        active_effects=s.active_effects,
        is_party=s.is_party,
    )
