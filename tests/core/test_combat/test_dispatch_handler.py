from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.action_economy import ActionEconomy
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.damage import DamageResult
from src.core.combat.dispatch_handler import DispatchTurnHandler

MODS = ClassModifiers(
    hit_dice=10, mod_hp_flat=0, mod_hp_mult=10, mana_multiplier=6,
    mod_atk_physical=10, mod_atk_magical=6, mod_def_physical=5,
    mod_def_magical=3, regen_hp_mod=5, regen_mana_mod=3,
)
EMPTY = ThresholdCalculator({})


def _make_char(name: str) -> Character:
    attrs = Attributes({
        AttributeType.STRENGTH: 5, AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 5, AttributeType.INTELLIGENCE: 5,
        AttributeType.WISDOM: 5, AttributeType.CHARISMA: 5,
        AttributeType.MIND: 5,
    })
    config = CharacterConfig(class_modifiers=MODS, threshold_calculator=EMPTY)
    return Character(name, attrs, config)


DUMMY_DAMAGE = DamageResult(raw_damage=0, defense_value=0, is_critical=False, final_damage=0)


class _NoopHandler:
    """Handler que nao faz nada, retorna evento marcador."""

    def __init__(self, tag: str) -> None:
        self._tag = tag

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=self._tag,
            target_name="none",
            damage=DUMMY_DAMAGE,
        )]


class TestDispatchHandler:
    def test_dispatches_to_registered_handler(self):
        special = _NoopHandler("special")
        default = _NoopHandler("default")
        dispatch = DispatchTurnHandler({"Alpha": special}, default)
        alpha = _make_char("Alpha")
        ctx = TurnContext(
            combatant=alpha, allies=[], enemies=[],
            action_economy=ActionEconomy(), round_number=1,
        )
        events = dispatch.execute_turn(ctx)
        assert events[0].actor_name == "special"

    def test_falls_back_to_default(self):
        special = _NoopHandler("special")
        default = _NoopHandler("default")
        dispatch = DispatchTurnHandler({"Alpha": special}, default)
        bravo = _make_char("Bravo")
        ctx = TurnContext(
            combatant=bravo, allies=[], enemies=[],
            action_economy=ActionEconomy(), round_number=1,
        )
        events = dispatch.execute_turn(ctx)
        assert events[0].actor_name == "default"

    def test_multiple_handlers(self):
        handler_a = _NoopHandler("handler_a")
        handler_b = _NoopHandler("handler_b")
        default = _NoopHandler("default")
        dispatch = DispatchTurnHandler(
            {"Alpha": handler_a, "Bravo": handler_b}, default,
        )
        alpha = _make_char("Alpha")
        bravo = _make_char("Bravo")
        ctx_a = TurnContext(
            combatant=alpha, allies=[], enemies=[],
            action_economy=ActionEconomy(), round_number=1,
        )
        ctx_b = TurnContext(
            combatant=bravo, allies=[], enemies=[],
            action_economy=ActionEconomy(), round_number=1,
        )
        assert dispatch.execute_turn(ctx_a)[0].actor_name == "handler_a"
        assert dispatch.execute_turn(ctx_b)[0].actor_name == "handler_b"

    def test_empty_handlers_always_uses_default(self):
        default = _NoopHandler("default")
        dispatch = DispatchTurnHandler({}, default)
        char = _make_char("Anyone")
        ctx = TurnContext(
            combatant=char, allies=[], enemies=[],
            action_economy=ActionEconomy(), round_number=1,
        )
        events = dispatch.execute_turn(ctx)
        assert events[0].actor_name == "default"
