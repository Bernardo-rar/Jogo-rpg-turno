"""Fixtures compartilhadas para testes de AI handlers."""

from __future__ import annotations

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.combat_engine import TurnContext
from src.core.characters.position import Position
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from tests.core.test_combat.conftest import _build_char

# Defaults de SkillEffect por tipo — garante que o applier funcione.
_EFFECT_DEFAULTS: dict[SkillEffectType, dict] = {
    SkillEffectType.BUFF: {"stat": ModifiableStat.PHYSICAL_ATTACK, "duration": 2},
    SkillEffectType.DEBUFF: {"stat": ModifiableStat.PHYSICAL_DEFENSE, "duration": 2},
    SkillEffectType.APPLY_AILMENT: {"ailment_id": "poison", "duration": 3},
}


def make_char(
    name: str = "Char",
    position: Position = Position.FRONT,
    speed: int = 10,
) -> object:
    """Cria Character de teste com posicao configuravel."""
    char = _build_char(name, speed=speed)
    char._position = position
    return char


def make_skill(
    skill_id: str = "test_skill",
    name: str = "Test Skill",
    mana_cost: int = 0,
    action_type: ActionType = ActionType.ACTION,
    target_type: TargetType = TargetType.SINGLE_ENEMY,
    effect_type: SkillEffectType = SkillEffectType.DAMAGE,
    base_power: int = 10,
    slot_cost: int = 1,
    **extra_effect_kwargs,
) -> Skill:
    """Cria Skill de teste com defaults que o applier aceita."""
    effect_kwargs: dict = {"effect_type": effect_type, "base_power": base_power}
    effect_kwargs.update(_EFFECT_DEFAULTS.get(effect_type, {}))
    effect_kwargs.update(extra_effect_kwargs)
    return Skill(
        skill_id=skill_id,
        name=name,
        mana_cost=mana_cost,
        action_type=action_type,
        target_type=target_type,
        effects=(SkillEffect(**effect_kwargs),),
        slot_cost=slot_cost,
    )


def make_bar(*skills: Skill) -> SkillBar:
    """Cria SkillBar com as skills dadas."""
    from src.core.skills.spell_slot import SpellSlot
    slot = SpellSlot(max_cost=99, skills=skills)
    return SkillBar(slots=(slot,))


def make_context(
    combatant,
    allies: list | None = None,
    enemies: list | None = None,
    round_number: int = 1,
) -> TurnContext:
    """Cria TurnContext com defaults uteis."""
    if allies is None:
        allies = [combatant]
    if enemies is None:
        enemies = [make_char("Enemy")]
    return TurnContext(
        combatant=combatant,
        allies=allies,
        enemies=enemies,
        action_economy=ActionEconomy(),
        round_number=round_number,
    )
