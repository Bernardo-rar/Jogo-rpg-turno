from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.core.combat.passive_manager import PassiveManager
    from src.core.combat.synergy.synergy_manager import SynergyManager
    from src.core.elements.element_type import ElementType

from src.core.characters.character import Character
from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.damage import DamageResult
from src.core.combat.effect_phase import (
    EffectLogEntry,
    apply_tick_results,
    create_skip_entry,
    process_effect_ticks,
    should_skip_turn,
)
from src.core.combat.reaction_system import ReactionHandler
from src.core.effects.tick_result import TickResult
from src.core.combat.turn_order import Combatant, TurnOrder

MAX_ROUNDS = 100
DEFAULT_SKIP_MESSAGE = "Cannot act"


class CombatResult(Enum):
    """Resultado final do combate."""

    PARTY_VICTORY = auto()
    PARTY_DEFEAT = auto()
    DRAW = auto()


class EventType(Enum):
    """Tipo de evento de combate."""

    DAMAGE = auto()
    HEAL = auto()
    BUFF = auto()
    DEBUFF = auto()
    AILMENT = auto()
    CLEANSE = auto()
    MANA_RESTORE = auto()
    FLEE = auto()
    SKILL_USE = auto()
    ITEM_USE = auto()
    SUMMON = auto()
    FIELD_EFFECT = auto()
    CHARGE = auto()
    TRANSFORM = auto()
    EMPOWER = auto()


@dataclass(frozen=True)
class CombatEvent:
    """Registro imutavel de algo que aconteceu no combate."""

    round_number: int
    actor_name: str
    target_name: str
    damage: DamageResult | None = None
    event_type: EventType = EventType.DAMAGE
    value: int = 0
    description: str = ""
    element: ElementType | None = None


@dataclass(frozen=True)
class TurnContext:
    """Contexto imutavel passado ao TurnHandler para decidir e executar acao."""

    combatant: Character
    allies: list[Character]
    enemies: list[Character]
    action_economy: ActionEconomy
    round_number: int


@dataclass(frozen=True)
class TurnStepResult:
    """Resultado imutavel de prepare_turn: contexto pronto ou motivo do skip."""

    can_act: bool
    context: TurnContext | None
    effect_entries: tuple[EffectLogEntry, ...]
    skip_reason: str = ""


class TurnHandler(Protocol):
    """Strategy: decide e executa a acao de um combatente no turno."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]: ...


class CombatEngine:
    """Motor de combate por turnos. Orquestra rounds, turnos e win/lose."""

    def __init__(
        self,
        party: list[Character],
        enemies: list[Character],
        turn_handler: TurnHandler,
        reaction_manager: ReactionHandler | None = None,
        passive_manager: PassiveManager | None = None,
        synergy_manager: SynergyManager | None = None,
    ) -> None:
        self._party = party
        self._enemies = enemies
        self._handler = turn_handler
        self._reaction_manager = reaction_manager
        self._synergy_manager = synergy_manager
        all_combatants = party + enemies
        _validate_unique_names(all_combatants)
        self._turn_order = TurnOrder(all_combatants)
        self._economies = {c.name: ActionEconomy() for c in all_combatants}
        self._participants = {c.name: c for c in all_combatants}
        self._round = 0
        self._events: list[CombatEvent] = []
        self._effect_log: list[EffectLogEntry] = []
        self._result: CombatResult | None = None
        self._passive_dispatcher = _build_passive_dispatcher(
            passive_manager, self._participants, party, enemies,
        )

    def add_combatant(
        self, character: Character, *, is_enemy: bool,
    ) -> None:
        """Adds a combatant mid-combat (for boss summons)."""
        if character.name in self._participants:
            raise ValueError("Combatant names must be unique")
        target_list = self._enemies if is_enemy else self._party
        target_list.append(character)
        self._participants[character.name] = character
        self._economies[character.name] = ActionEconomy()
        self._turn_order.insert(character)

    def start_round(self) -> None:
        """Incrementa round e reseta turn order."""
        self._round += 1
        self._turn_order.reset()
        if self._passive_dispatcher is not None:
            self._events.extend(
                self._passive_dispatcher.fire_round_start(self._round),
            )
        _refresh_synergy_auras(
            self._synergy_manager, self._enemies, self._participants,
        )

    def get_next_combatant(self) -> str | None:
        """Retorna nome do proximo combatente ou None se round acabou."""
        proto = self._turn_order.next()
        return proto.name if proto is not None else None

    def prepare_turn(self, combatant_name: str) -> TurnStepResult:
        """Fase 1: reset economy, tick effects, check skip."""
        combatant = self._participants[combatant_name]
        economy = self._economies[combatant_name]
        economy.reset()
        _tick_cooldowns(combatant)
        tick_results = process_effect_ticks(combatant.effect_manager)
        entries = tuple(
            apply_tick_results(combatant, tick_results, self._round),
        )
        self._effect_log.extend(entries)
        skip = should_skip_turn(tick_results)
        if not combatant.is_alive or skip:
            return _build_skip_result(
                combatant, tick_results, entries,
                self._round, self._effect_log,
            )
        context = _build_context(
            combatant, economy,
            self._party, self._enemies, self._round,
        )
        return TurnStepResult(
            can_act=True, context=context, effect_entries=entries,
        )

    def resolve_turn(self, events: list[CombatEvent]) -> CombatResult | None:
        """Fase 2: registra eventos, dispara passivas e checa vitoria."""
        self._events.extend(events)
        if self._passive_dispatcher is not None:
            self._events.extend(
                self._passive_dispatcher.fire_event_passives(
                    events, self._round,
                ),
            )
        _fire_synergy_deaths(
            self._synergy_manager, events,
            self._participants, self._events, self._round,
        )
        _process_pending_summons(
            self._handler, self._enemies,
            self.add_combatant, self._events, self._round,
        )
        self._result = _check_result(self._party, self._enemies)
        return self._result

    def run_round(self) -> CombatResult | None:
        """Executa uma rodada completa."""
        self.start_round()
        name = self.get_next_combatant()
        while name is not None:
            step = self.prepare_turn(name)
            if step.can_act:
                self._events.extend(
                    self._handler.execute_turn(step.context),
                )
            self._result = _check_result(self._party, self._enemies)
            if self._result is not None:
                return self._result
            name = self.get_next_combatant()
        return self._result

    def run_combat(self) -> CombatResult:
        """Executa combate completo ate vitoria, derrota ou empate."""
        while self._round < MAX_ROUNDS:
            result = self.run_round()
            if result is not None:
                return result
        self._result = CombatResult.DRAW
        return self._result

    def process_damage_reactions(
        self, events: list[CombatEvent],
    ) -> list[CombatEvent]:
        """Checa reacoes para eventos de dano."""
        if self._reaction_manager is None:
            return []
        return _process_reactions(
            self._reaction_manager, events,
            self._participants, self._economies, self._round,
        )

    @property
    def round_number(self) -> int:
        return self._round

    @property
    def events(self) -> list[CombatEvent]:
        return list(self._events)

    @property
    def result(self) -> CombatResult | None:
        return self._result

    @property
    def effect_log(self) -> list[EffectLogEntry]:
        return list(self._effect_log)

    @property
    def turn_order_names(self) -> list[str]:
        """Nomes dos combatentes vivos na ordem de turno do round atual."""
        return [c.name for c in self._turn_order.get_order()]


# --- Module-level helpers ---


def _validate_unique_names(combatants: list[Character]) -> None:
    names = [c.name for c in combatants]
    if len(names) != len(set(names)):
        raise ValueError("Combatant names must be unique")


def _build_passive_dispatcher(
    passive_manager: PassiveManager | None,
    participants: dict[str, Character],
    party: list[Character],
    enemies: list[Character],
) -> object | None:
    """Creates a PassiveEventDispatcher if passive_manager exists."""
    if passive_manager is None:
        return None
    from src.core.combat.passive_event_dispatcher import (
        PassiveEventDispatcher,
    )
    return PassiveEventDispatcher(
        passive_manager, participants, party, enemies,
    )


def _build_context(
    combatant: Character,
    economy: ActionEconomy,
    party: list[Character],
    enemies: list[Character],
    round_number: int,
) -> TurnContext:
    """Builds a TurnContext for the given combatant."""
    if combatant in party:
        allies, foes = party, enemies
    else:
        allies, foes = enemies, party
    return TurnContext(
        combatant=combatant, allies=allies, enemies=foes,
        action_economy=economy, round_number=round_number,
    )


def _build_skip_result(
    combatant: Character,
    tick_results: list[TickResult],
    entries: tuple[EffectLogEntry, ...],
    round_number: int,
    effect_log: list[EffectLogEntry],
) -> TurnStepResult:
    """Builds a skip TurnStepResult and logs if applicable."""
    if not combatant.is_alive:
        reason = "Dead"
    else:
        reason = _extract_skip_message(tick_results)
        effect_log.append(
            create_skip_entry(combatant.name, round_number, reason),
        )
    return TurnStepResult(
        can_act=False, context=None,
        effect_entries=entries, skip_reason=reason,
    )


def _tick_cooldowns(combatant: Character) -> None:
    """Decrementa cooldowns do combatente se tiver skill_bar."""
    bar = combatant.skill_bar
    if bar is not None:
        bar.cooldown_tracker.tick()


def _extract_skip_message(tick_results: list[TickResult]) -> str:
    """Extrai mensagem de skip dos tick results, ou retorna default."""
    skip_msgs = [r.message for r in tick_results if r.skip_turn]
    return skip_msgs[0] if skip_msgs else DEFAULT_SKIP_MESSAGE


def _refresh_synergy_auras(
    synergy_manager: SynergyManager | None,
    enemies: list[Character],
    participants: dict[str, Character],
) -> None:
    """Refreshes commander auras for alive commanders."""
    if synergy_manager is None:
        return
    from src.core.combat.synergy.synergy_behaviors import (
        apply_commander_aura,
    )
    for enemy in enemies:
        if not enemy.is_alive:
            continue
        aura_cfg = synergy_manager.get_commander_aura(enemy.name)
        if aura_cfg is None:
            continue
        members = synergy_manager.get_synergy_members(enemy.name)
        followers = [
            participants[n]
            for n in members
            if n != enemy.name and n in participants
        ]
        apply_commander_aura(followers, aura_cfg)


def _fire_synergy_deaths(
    synergy_manager: SynergyManager | None,
    events: list[CombatEvent],
    participants: dict[str, Character],
    event_log: list[CombatEvent],
    round_number: int,
) -> None:
    """Fires synergy on_death for dead enemies."""
    if synergy_manager is None:
        return
    fired: set[str] = set()
    for event in events:
        target = participants.get(event.target_name)
        if target is None or target.is_alive:
            continue
        if event.target_name in fired:
            continue
        fired.add(event.target_name)
        event_log.extend(
            synergy_manager.on_death(event.target_name, round_number),
        )


def _process_pending_summons(
    handler: TurnHandler,
    enemies: list[Character],
    add_combatant_fn: object,
    event_log: list[CombatEvent],
    round_number: int,
) -> None:
    """Checks handler for pending summons and spawns minions."""
    from src.core.combat.minion_spawner import (
        SpawnContext,
        process_pending_summons,
        spawn_minion,
    )
    ctx = SpawnContext(enemies, handler, add_combatant_fn, round_number)

    def _spawn(summon_cfg: object) -> None:
        result = spawn_minion(summon_cfg, ctx)
        if result is not None:
            event_log.append(result)

    process_pending_summons(handler, _spawn)


def _check_result(
    party: list[Character],
    enemies: list[Character],
) -> CombatResult | None:
    """Checks if combat is over."""
    party_alive = any(c.is_alive for c in party)
    enemies_alive = any(c.is_alive for c in enemies)
    if not enemies_alive:
        return CombatResult.PARTY_VICTORY
    if not party_alive:
        return CombatResult.PARTY_DEFEAT
    return None


def _process_reactions(
    reaction_manager: ReactionHandler,
    events: list[CombatEvent],
    participants: dict[str, Character],
    economies: dict[str, ActionEconomy],
    round_number: int,
) -> list[CombatEvent]:
    """Processes damage reactions for all events."""
    from src.core.combat.reaction_system import ReactionTrigger

    reaction_events: list[CombatEvent] = []
    for event in events:
        if event.damage is None:
            continue
        target = participants.get(event.target_name)
        if target is None or not target.is_alive:
            continue
        economy = economies.get(event.target_name)
        if economy is None:
            continue
        reaction_events.extend(
            reaction_manager.check_trigger(
                trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
                target=target,
                economy=economy,
                round_number=round_number,
            ),
        )
    return reaction_events
