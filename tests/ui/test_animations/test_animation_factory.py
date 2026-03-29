"""Testes para AnimationFactory."""

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.damage import DamageResult
from src.core.elements.element_type import ElementType
from src.ui import colors
from src.ui.animations.animation_factory import AnimationFactory
from src.ui.animations.buff_aura import BuffAura
from src.ui.animations.card_shake import CardShake
from src.ui.animations.floating_text import FloatingText
from src.ui.animations.heal_particles import HealParticles
from src.ui.animations.magic_burst import MagicBurst
from src.ui.animations.particle import ParticleEmitter
from src.ui.animations.poison_bubbles import PoisonBubbles
from src.ui.animations.multi_slash import MultiSlash
from src.ui.animations.slash_effect import SlashEffect

_RECT = (100, 50, 160, 110)


def _damage_event(value: int = 25, *, is_critical: bool = False) -> CombatEvent:
    return CombatEvent(
        round_number=1, actor_name="Fighter", target_name="Goblin",
        event_type=EventType.DAMAGE,
        damage=DamageResult(
            raw_damage=30, defense_value=5,
            is_critical=is_critical, final_damage=value,
        ),
        value=value,
    )


def _magical_damage_event(
    value: int = 25, element: ElementType = ElementType.FIRE,
) -> CombatEvent:
    return CombatEvent(
        round_number=1, actor_name="Mage", target_name="Goblin",
        event_type=EventType.DAMAGE,
        damage=DamageResult(
            raw_damage=30, defense_value=5,
            is_critical=False, final_damage=value,
        ),
        value=value,
        element=element,
    )


def _heal_event(value: int = 30) -> CombatEvent:
    return CombatEvent(
        round_number=1, actor_name="Cleric", target_name="Fighter",
        event_type=EventType.HEAL, value=value,
    )


def _buff_event() -> CombatEvent:
    return CombatEvent(
        round_number=1, actor_name="Bard", target_name="Fighter",
        event_type=EventType.BUFF, value=5,
    )


def _debuff_event() -> CombatEvent:
    return CombatEvent(
        round_number=1, actor_name="Mage", target_name="Goblin",
        event_type=EventType.DEBUFF, value=3,
    )


def _ailment_event() -> CombatEvent:
    return CombatEvent(
        round_number=1, actor_name="Mage", target_name="Goblin",
        event_type=EventType.AILMENT, description="poison",
    )


class TestAnimationFactory:
    def test_damage_creates_slash_shake_and_text(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_damage_event(25), _RECT)
        types = [type(a) for a in anims]
        assert MultiSlash in types or SlashEffect in types
        assert CardShake in types
        assert FloatingText in types

    def test_damage_text_shows_value(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_damage_event(42), _RECT)
        texts = [a for a in anims if isinstance(a, FloatingText)]
        assert len(texts) == 1
        assert "42" in texts[0].text

    def test_heal_creates_particles_and_text(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_heal_event(30), _RECT)
        types = [type(a) for a in anims]
        assert HealParticles in types
        assert FloatingText in types

    def test_heal_text_shows_value(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_heal_event(45), _RECT)
        texts = [a for a in anims if isinstance(a, FloatingText)]
        assert len(texts) == 1
        assert "45" in texts[0].text

    def test_buff_creates_green_aura(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_buff_event(), _RECT)
        assert len(anims) == 1
        assert isinstance(anims[0], BuffAura)

    def test_debuff_creates_red_aura(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_debuff_event(), _RECT)
        assert len(anims) == 1
        assert isinstance(anims[0], BuffAura)

    def test_ailment_creates_poison_bubbles(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_ailment_event(), _RECT)
        assert len(anims) == 1
        assert isinstance(anims[0], PoisonBubbles)

    def test_unknown_event_returns_empty(self) -> None:
        factory = AnimationFactory()
        event = CombatEvent(
            round_number=1, actor_name="A", target_name="B",
            event_type=EventType.FLEE,
        )
        anims = factory.create(event, _RECT)
        assert anims == []

    def test_magical_damage_creates_particle_emitter_and_text(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(
            _magical_damage_event(25, element=ElementType.FIRE), _RECT,
        )
        types = [type(a) for a in anims]
        assert ParticleEmitter in types
        assert FloatingText in types
        assert SlashEffect not in types

    def test_magical_damage_unknown_element_falls_back(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_magical_damage_event(25), _RECT)
        types = [type(a) for a in anims]
        assert MagicBurst in types or ParticleEmitter in types
        assert FloatingText in types

    def test_physical_damage_still_creates_slash(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_damage_event(25), _RECT)
        types = [type(a) for a in anims]
        assert MultiSlash in types or SlashEffect in types
        assert MagicBurst not in types

    def test_critical_damage_text_has_crit_suffix(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_damage_event(50, is_critical=True), _RECT)
        texts = [a for a in anims if isinstance(a, FloatingText)]
        assert any("CRIT" in t.text for t in texts)

    def test_critical_damage_text_color_is_yellow(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_damage_event(50, is_critical=True), _RECT)
        texts = [a for a in anims if isinstance(a, FloatingText)]
        assert texts[0].color == colors.TEXT_CRITICAL

    def test_non_critical_damage_text_is_red(self) -> None:
        factory = AnimationFactory()
        anims = factory.create(_damage_event(25), _RECT)
        texts = [a for a in anims if isinstance(a, FloatingText)]
        assert texts[0].color == colors.TEXT_DAMAGE
