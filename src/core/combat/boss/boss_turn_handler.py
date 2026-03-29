"""BossTurnHandler — orchestrates advanced boss mechanics per turn."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.boss.boss_field_effect import BossFieldEffect
from src.core.combat.boss.boss_mechanic_config import (
    BossMechanicConfig,
    SummonConfig,
)

from src.core.combat.boss.boss_transformation import (
    TransformationConfig,
    apply_transformation,
)
from src.core.combat.boss.charged_attack import (
    ChargeStateEffect,
    ChargedAttackConfig,
)
from src.core.combat.boss.empower_bar import EmpowerBar
from src.core.combat.damage import resolve_damage
from src.core.effects.buff_factory import create_percent_buff
from src.core.effects.modifiable_stat import ModifiableStat

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.combat.combat_engine import CombatEvent, TurnContext, TurnHandler

EMPOWER_BUFF_SOURCE = "boss_empower"
ENRAGE_BUFF_DURATION = 999


class BossTurnHandler:
    """Wraps a base TurnHandler with boss-specific mechanics.

    Turn flow:
      1. Check for pending charged attack release
      2. Tick empower bar, check empowered state
      3. Maybe start a charged attack (skips normal turn)
      4. Otherwise delegate to base handler
    """

    def __init__(
        self,
        base_handler: TurnHandler,
        config: BossMechanicConfig,
    ) -> None:
        self._base = base_handler
        self._config = config
        self._empower = (
            EmpowerBar(config.empower_bar)
            if config.empower_bar else None
        )
        self._charge_pending: ChargedAttackConfig | None = None
        self._last_charge_round: int = 0
        self._last_summon_round: int = 0
        self._transformed: bool = False
        self._field_active: BossFieldEffect | None = None
        self._minion_names: list[str] = []
        self._pending_summons: list[SummonConfig] = []

    @property
    def empower_bar(self) -> EmpowerBar | None:
        return self._empower

    @property
    def is_transformed(self) -> bool:
        return self._transformed

    @property
    def field_effect(self) -> BossFieldEffect | None:
        return self._field_active

    def drain_pending_summons(self) -> list[SummonConfig]:
        """Returns and clears pending summon requests."""
        result = list(self._pending_summons)
        self._pending_summons.clear()
        return result

    def request_summon(self, config: SummonConfig) -> None:
        """Queues a summon request for the engine to process."""
        self._pending_summons.append(config)

    def execute_turn(
        self, context: TurnContext,
    ) -> list[CombatEvent]:
        """Boss turn with all mechanic layers."""
        from src.core.combat.combat_engine import CombatEvent, EventType

        events: list[CombatEvent] = []

        events.extend(self._tick_field(context))
        events.extend(self._tick_empower(context))
        events.extend(self._check_transform(context))

        released = self._try_release_charge(context)
        if released:
            return events + released

        charge_started = self._try_start_charge(context)
        if charge_started:
            return events + charge_started

        turn_events = self._base.execute_turn(context)
        return events + turn_events

    def on_minion_death(
        self, boss: Character, minion_name: str,
    ) -> list[CombatEvent]:
        """Called when a summoned minion dies. Enrages the boss."""
        from src.core.combat.combat_engine import CombatEvent, EventType

        if minion_name in self._minion_names:
            self._minion_names.remove(minion_name)
        cfg = self._config.summons[0] if self._config.summons else None
        if cfg is None:
            return []
        buff = create_percent_buff(
            stat=ModifiableStat.PHYSICAL_ATTACK,
            percent=cfg.enrage_atk_pct,
            duration=ENRAGE_BUFF_DURATION,
        )
        boss.effect_manager.add_effect(buff)
        return [CombatEvent(
            round_number=0,
            actor_name=boss.name,
            target_name=boss.name,
            event_type=EventType.BUFF,
            description="Enraged by minion death!",
        )]

    def on_weakness_hit(self) -> None:
        """Reduces empower bar when boss is hit by weakness element."""
        if self._empower is not None:
            self._empower.on_weakness_hit()

    def _tick_empower(
        self, context: TurnContext,
    ) -> list[CombatEvent]:
        from src.core.combat.combat_engine import CombatEvent, EventType

        if self._empower is None:
            return []
        events: list[CombatEvent] = []
        if self._empower.is_empowered:
            ended = self._empower.tick_empowered()
            if ended:
                events.append(CombatEvent(
                    round_number=context.round_number,
                    actor_name=context.combatant.name,
                    target_name=context.combatant.name,
                    event_type=EventType.EMPOWER,
                    description="Empowered state fades.",
                ))
            return events
        became_full = self._empower.tick_round()
        if became_full:
            self._empower.activate_empowered()
            events.append(CombatEvent(
                round_number=context.round_number,
                actor_name=context.combatant.name,
                target_name=context.combatant.name,
                event_type=EventType.EMPOWER,
                description="Boss becomes EMPOWERED!",
            ))
        return events

    def _tick_field(
        self, context: TurnContext,
    ) -> list[CombatEvent]:
        """Applies field damage to all enemies (the player party)."""
        from src.core.combat.combat_engine import CombatEvent, EventType

        if self._field_active is None:
            return []
        if self._field_active.is_expired:
            self._field_active = None
            return []
        self._field_active.tick()
        events: list[CombatEvent] = []
        for target in context.enemies:
            if not target.is_alive:
                continue
            dmg = self._field_active.compute_damage(target.max_hp)
            target.take_damage(dmg)
            events.append(CombatEvent(
                round_number=context.round_number,
                actor_name=context.combatant.name,
                target_name=target.name,
                event_type=EventType.FIELD_EFFECT,
                description=self._field_active.config.name,
                value=dmg,
            ))
        return events

    def _check_transform(
        self, context: TurnContext,
    ) -> list[CombatEvent]:
        from src.core.combat.combat_engine import CombatEvent, EventType

        cfg = self._config.transformation
        if cfg is None or self._transformed:
            return []
        ratio = _hp_ratio(context.combatant)
        if ratio > cfg.hp_threshold:
            return []
        self._transformed = True
        apply_transformation(context.combatant, cfg)
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=context.combatant.name,
            event_type=EventType.TRANSFORM,
            description=cfg.battle_cry,
        )]

    def _try_release_charge(
        self, context: TurnContext,
    ) -> list[CombatEvent] | None:
        if self._charge_pending is None:
            return None
        cfg = self._charge_pending
        self._charge_pending = None
        return _release_charged_attack(cfg, context)

    def _try_start_charge(
        self, context: TurnContext,
    ) -> list[CombatEvent] | None:
        from src.core.combat.combat_engine import CombatEvent, EventType

        if not self._config.charged_attacks:
            return None
        interval = self._config.charge_every_n_rounds
        since_last = context.round_number - self._last_charge_round
        if since_last < interval:
            return None
        cfg = self._config.charged_attacks[0]
        self._charge_pending = cfg
        self._last_charge_round = context.round_number
        effect = ChargeStateEffect(cfg)
        context.combatant.effect_manager.add_effect(effect)
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=context.combatant.name,
            event_type=EventType.CHARGE,
            description=cfg.charge_message,
        )]

    def activate_field(self, field_cfg: BossFieldConfig) -> None:
        """Activates a field effect (replaces any existing)."""
        self._field_active = BossFieldEffect(field_cfg)

    def register_minion(self, name: str) -> None:
        """Tracks a summoned minion name."""
        self._minion_names.append(name)

    def alive_minion_count(
        self, enemies: list[Character],
    ) -> int:
        """Counts how many tracked minions are still alive."""
        alive_names = {e.name for e in enemies if e.is_alive}
        return sum(1 for n in self._minion_names if n in alive_names)


def _release_charged_attack(
    cfg: ChargedAttackConfig,
    context: TurnContext,
) -> list[CombatEvent]:
    """Fires a charged attack at targets."""
    from src.core.combat.combat_engine import CombatEvent, EventType

    boss = context.combatant
    base_atk = boss.attack_power
    boosted = int(base_atk * cfg.damage_mult)
    targets = [e for e in context.enemies if e.is_alive]
    if cfg.target_type == "SINGLE_ENEMY" and targets:
        targets = [targets[0]]
    events: list[CombatEvent] = []
    for i, target in enumerate(targets):
        mult = cfg.aoe_falloff ** i if i > 0 else 1.0
        atk = max(1, int(boosted * mult))
        def_type = boss.preferred_attack_type
        result = resolve_damage(
            attack_power=atk, defense=target.defense_for(def_type),
        )
        target.take_damage(result.final_damage)
        events.append(CombatEvent(
            round_number=context.round_number,
            actor_name=boss.name,
            target_name=target.name,
            damage=result,
            event_type=EventType.CHARGE,
            description=cfg.release_message,
        ))
    return events


def _hp_ratio(boss: Character) -> float:
    if boss.max_hp == 0:
        return 0.0
    return boss.current_hp / boss.max_hp
