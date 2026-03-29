"""SynergyManager — tracks enemy synergy relationships in combat."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.synergy.synergy_config import (
    CommanderAuraConfig,
    DeathEffect,
    SynergyBinding,
    SynergyConfig,
    SynergyType,
)
from src.core.effects.buff_factory import (
    create_percent_buff,
    create_percent_debuff,
)
from src.core.effects.modifiable_stat import ModifiableStat

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.combat.combat_engine import CombatEvent

SYNERGY_SOURCE = "synergy"


class SynergyManager:
    """Tracks synergy bindings between enemy combatants."""

    def __init__(
        self,
        synergies: dict[str, SynergyConfig],
        bindings: list[SynergyBinding],
        combatants: list[Character],
    ) -> None:
        self._synergies = synergies
        self._bindings = bindings
        self._chars = {c.name: c for c in combatants}

    def get_partner(self, name: str) -> str | None:
        """Returns partner name for a PAIR synergy, or None."""
        binding = self._find_binding(name)
        if binding is None:
            return None
        cfg = self._synergies.get(binding.synergy_id)
        if cfg is None or cfg.synergy_type != SynergyType.PAIR:
            return None
        for other in self._bindings:
            if (other.synergy_id == binding.synergy_id
                    and other.combatant_name != name):
                return other.combatant_name
        return None

    def get_group_members(self, name: str) -> list[str]:
        """Returns all names in the same GROUP synergy."""
        binding = self._find_binding(name)
        if binding is None:
            return []
        return [
            b.combatant_name for b in self._bindings
            if b.synergy_id == binding.synergy_id
        ]

    def is_commander(self, name: str) -> bool:
        """True if this combatant has the 'commander' role."""
        binding = self._find_binding(name)
        return binding is not None and binding.role_key == "commander"

    def get_commander_aura(
        self, name: str,
    ) -> CommanderAuraConfig | None:
        """Returns aura config if this combatant is a commander."""
        binding = self._find_binding(name)
        if binding is None or binding.role_key != "commander":
            return None
        cfg = self._synergies.get(binding.synergy_id)
        if cfg is None:
            return None
        return cfg.commander_aura

    def get_synergy_members(self, name: str) -> list[str]:
        """Returns all combatant names in the same synergy."""
        binding = self._find_binding(name)
        if binding is None:
            return []
        return [
            b.combatant_name for b in self._bindings
            if b.synergy_id == binding.synergy_id
        ]

    def on_death(
        self, dead_name: str, round_number: int,
    ) -> list[CombatEvent]:
        """Processes synergy effects when a member dies."""
        binding = self._find_binding(dead_name)
        if binding is None:
            return []
        cfg = self._synergies.get(binding.synergy_id)
        if cfg is None:
            return []
        if cfg.synergy_type == SynergyType.PAIR:
            return self._on_pair_death(
                dead_name, binding, cfg, round_number,
            )
        if cfg.synergy_type == SynergyType.GROUP:
            return self._on_group_death(
                dead_name, binding, cfg, round_number,
            )
        if cfg.synergy_type == SynergyType.COMMANDER:
            return self._on_commander_death(
                dead_name, binding, cfg, round_number,
            )
        return []

    def _on_pair_death(
        self,
        dead_name: str,
        binding: SynergyBinding,
        cfg: SynergyConfig,
        round_number: int,
    ) -> list[CombatEvent]:
        partner_name = self.get_partner(dead_name)
        if partner_name is None:
            return []
        partner = self._chars.get(partner_name)
        if partner is None or not partner.is_alive:
            return []
        dead_role = self._find_role(cfg, binding.role_key)
        partner_binding = self._find_binding(partner_name)
        partner_role = (
            self._find_role(cfg, partner_binding.role_key)
            if partner_binding else None
        )
        effects = (
            partner_role.on_partner_death_buffs
            if partner_role else ()
        )
        return _apply_death_effects(
            partner, effects, round_number,
        )

    def _on_group_death(
        self,
        dead_name: str,
        binding: SynergyBinding,
        cfg: SynergyConfig,
        round_number: int,
    ) -> list[CombatEvent]:
        members = self.get_group_members(dead_name)
        alive = [
            self._chars[n] for n in members
            if n != dead_name and n in self._chars
            and self._chars[n].is_alive
        ]
        if len(alive) != 1 or cfg.last_survivor is None:
            return []
        survivor = alive[0]
        ls = cfg.last_survivor
        effects = (
            DeathEffect("PHYSICAL_ATTACK", ls.atk_bonus_pct, ls.duration),
            DeathEffect("SPEED", ls.speed_bonus_pct, ls.duration),
        )
        return _apply_death_effects(survivor, effects, round_number)

    def _on_commander_death(
        self,
        dead_name: str,
        binding: SynergyBinding,
        cfg: SynergyConfig,
        round_number: int,
    ) -> list[CombatEvent]:
        if binding.role_key != "commander":
            return []
        if cfg.commander_death_debuff is None:
            return []
        events: list[CombatEvent] = []
        followers = [
            b for b in self._bindings
            if b.synergy_id == binding.synergy_id
            and b.combatant_name != dead_name
        ]
        for fb in followers:
            char = self._chars.get(fb.combatant_name)
            if char is not None and char.is_alive:
                events.extend(_apply_death_effects(
                    char,
                    (cfg.commander_death_debuff,),
                    round_number,
                ))
        return events

    def _find_binding(self, name: str) -> SynergyBinding | None:
        for b in self._bindings:
            if b.combatant_name == name:
                return b
        return None

    def _find_role(self, cfg, role_key):
        for role in cfg.roles:
            if role.role_key == role_key:
                return role
        return None


def _apply_death_effects(
    target: Character,
    effects: tuple[DeathEffect, ...] | list[DeathEffect],
    round_number: int,
) -> list[CombatEvent]:
    """Applies DeathEffects as StatBuffs and returns events."""
    from src.core.combat.combat_engine import CombatEvent, EventType

    events: list[CombatEvent] = []
    for de in effects:
        try:
            stat = ModifiableStat[de.stat]
        except KeyError:
            continue
        if de.percent >= 0:
            buff = create_percent_buff(
                stat=stat, percent=de.percent, duration=de.duration,
            )
        else:
            buff = create_percent_debuff(
                stat=stat, percent=abs(de.percent), duration=de.duration,
            )
        target.effect_manager.add_effect(buff)
        etype = EventType.BUFF if de.percent > 0 else EventType.DEBUFF
        events.append(CombatEvent(
            round_number=round_number,
            actor_name=target.name,
            target_name=target.name,
            event_type=etype,
            description=f"Synergy: {de.stat} {de.percent:+.0f}%",
        ))
    return events
