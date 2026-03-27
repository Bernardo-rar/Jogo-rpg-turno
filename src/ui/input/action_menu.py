"""ActionMenu — menu hierarquico que produz PlayerAction via teclas 1-9."""

from __future__ import annotations

from enum import Enum, auto

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import TurnContext
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.core.skills.class_resource_resolver import can_afford_resource
from src.core.skills.skill import Skill
from src.core.skills.target_type import TargetType
from src.ui.input.menu_state import MenuLevel, MenuOption

_AUTO_TARGET_TYPES = frozenset({
    TargetType.SELF, TargetType.ALL_ALLIES, TargetType.ALL_ENEMIES,
})

_LEVEL1_KEY_ACTION = 1
_LEVEL1_KEY_BONUS = 2
_LEVEL1_KEY_REACTION = 3
_LEVEL1_KEY_ITEM = 4
_LEVEL1_KEY_END_TURN = 5


class _Category(Enum):
    """Categoria selecionada no nivel 1."""

    ACTION = auto()
    BONUS = auto()
    REACTION = auto()
    ITEM = auto()


_CATEGORY_LABELS: dict[_Category, str] = {
    _Category.ACTION: "Action",
    _Category.BONUS: "Bonus Action",
    _Category.REACTION: "Reaction",
    _Category.ITEM: "Item",
}


class ActionMenu:
    """Menu hierarquico de 3 niveis que produz PlayerAction."""

    def __init__(self, context: TurnContext) -> None:
        self._context = context
        self._level = MenuLevel.ACTION_TYPE
        self._category: _Category | None = None
        self._pending_type: PlayerActionType | None = None
        self._pending_skill_id: str = ""
        self._pending_consumable_id: str = ""
        self._pending_target_type: TargetType = TargetType.SINGLE_ENEMY
        self._pending_action_label: str = ""
        self._options: list[MenuOption] = []
        self._tags: dict[int, str] = {}
        self._highlight_index: int = 0
        self._rebuild()

    @property
    def current_level(self) -> MenuLevel:
        return self._level

    @property
    def options(self) -> list[MenuOption]:
        return list(self._options)

    @property
    def pending_action_type(self) -> PlayerActionType | None:
        """Tipo de acao pendente no nivel 3 (target select)."""
        if self._level != MenuLevel.TARGET_SELECT:
            return None
        return self._pending_type

    @property
    def pending_skill(self) -> Skill | None:
        """Skill pendente no nivel 3 (target select)."""
        if not self._pending_skill_id:
            return None
        return _find_skill(self._pending_skill_id, self._context)

    @property
    def breadcrumb(self) -> str:
        """Returns navigation path like 'Action > Fireball'."""
        if self._level == MenuLevel.ACTION_TYPE:
            return ""
        cat_label = _CATEGORY_LABELS.get(self._category, "")
        if self._level == MenuLevel.SPECIFIC_ACTION:
            return cat_label
        return f"{cat_label} > {self._pending_action_label}"

    @property
    def highlight_index(self) -> int:
        return self._highlight_index

    @property
    def highlighted_skill(self) -> Skill | None:
        """Skill destacada no nivel SPECIFIC_ACTION (se houver)."""
        if self._level != MenuLevel.SPECIFIC_ACTION:
            return None
        return self._skill_at_highlight()

    def move_highlight(self, delta: int) -> None:
        """Move o highlight index para cima (-1) ou para baixo (+1)."""
        if not self._options:
            return
        total = len(self._options)
        self._highlight_index = (self._highlight_index + delta) % total

    def _skill_at_highlight(self) -> Skill | None:
        """Retorna a skill correspondente ao highlight_index atual."""
        if self._highlight_index >= len(self._options):
            return None
        key = self._options[self._highlight_index].key
        tag = self._tags.get(key, "")
        if not tag.startswith("skill:"):
            return None
        return _find_skill(tag[6:], self._context)

    def select(self, key: int) -> PlayerAction | None:
        """Processa tecla. Retorna PlayerAction se completo, None se nao."""
        tag = self._tags.get(key)
        if tag is None:
            return None
        opt = next((o for o in self._options if o.key == key), None)
        if opt is None or not opt.available:
            return None
        if self._level == MenuLevel.ACTION_TYPE:
            return self._handle_level1(tag)
        if self._level == MenuLevel.SPECIFIC_ACTION:
            return self._handle_level2(tag)
        return self._handle_level3(tag)

    def cancel(self) -> bool:
        """Volta um nivel. Retorna False se ja no topo."""
        if self._level == MenuLevel.ACTION_TYPE:
            return False
        if self._level == MenuLevel.TARGET_SELECT:
            self._level = MenuLevel.SPECIFIC_ACTION
        else:
            self._level = MenuLevel.ACTION_TYPE
            self._category = None
        self._rebuild()
        return True

    def _handle_level1(self, tag: str) -> PlayerAction | None:
        if tag == "end_turn":
            return PlayerAction(action_type=PlayerActionType.END_TURN)
        category_map = {
            "action": _Category.ACTION,
            "bonus": _Category.BONUS,
            "reaction": _Category.REACTION,
            "item": _Category.ITEM,
        }
        self._category = category_map[tag]
        self._level = MenuLevel.SPECIFIC_ACTION
        self._rebuild()
        return None

    def _handle_level2(self, tag: str) -> PlayerAction | None:
        if tag == "basic_attack":
            self._pending_action_label = PlayerActionType.BASIC_ATTACK.label
            return self._prepare_target_select(
                PlayerActionType.BASIC_ATTACK,
                TargetType.SINGLE_ENEMY,
            )
        if tag == "move":
            return PlayerAction(action_type=PlayerActionType.MOVE)
        if tag == "defend":
            return PlayerAction(action_type=PlayerActionType.DEFEND)
        if tag.startswith("skill:"):
            return self._handle_skill_select(tag[6:])
        if tag.startswith("item:"):
            return self._handle_item_select(tag[5:])
        return None

    def _handle_level3(self, tag: str) -> PlayerAction | None:
        return PlayerAction(
            action_type=self._pending_type,
            target_name=tag,
            skill_id=self._pending_skill_id,
            consumable_id=self._pending_consumable_id,
        )

    def _handle_skill_select(self, skill_id: str) -> PlayerAction | None:
        skill = _find_skill(skill_id, self._context)
        if skill is None:
            return None
        self._pending_action_label = skill.name
        return self._prepare_target_select(
            PlayerActionType.SKILL, skill.target_type,
            skill_id=skill_id,
        )

    def _handle_item_select(self, cid: str) -> PlayerAction | None:
        inv = self._context.combatant.inventory
        if inv is None:
            return None
        slot = inv.get_slot(cid)
        if slot is None:
            return None
        self._pending_action_label = slot.consumable.name
        return self._prepare_target_select(
            PlayerActionType.ITEM, slot.consumable.target_type,
            consumable_id=cid,
        )

    def _prepare_target_select(
        self, action_type: PlayerActionType,
        target_type: TargetType, *,
        skill_id: str = "", consumable_id: str = "",
    ) -> PlayerAction | None:
        if target_type in _AUTO_TARGET_TYPES:
            return PlayerAction(
                action_type=action_type,
                skill_id=skill_id,
                consumable_id=consumable_id,
            )
        self._pending_type = action_type
        self._pending_target_type = target_type
        self._pending_skill_id = skill_id
        self._pending_consumable_id = consumable_id
        self._level = MenuLevel.TARGET_SELECT
        self._rebuild()
        return None

    def _rebuild(self) -> None:
        """Reconstroi opcoes e tags para o nivel atual."""
        self._options = []
        self._tags = {}
        self._highlight_index = 0
        if self._level == MenuLevel.ACTION_TYPE:
            _build_level1(self._context, self._options, self._tags)
        elif self._level == MenuLevel.SPECIFIC_ACTION:
            _build_level2(
                self._category, self._context,
                self._options, self._tags,
            )
        else:
            _build_level3(
                self._context, self._pending_target_type,
                self._options, self._tags,
            )


def _build_level1(
    ctx: TurnContext,
    options: list[MenuOption], tags: dict[int, str],
) -> None:
    """Constroi opcoes do nivel 1: tipo de acao."""
    economy = ctx.action_economy
    if economy.is_available(ActionType.ACTION):
        _add(options, tags, _LEVEL1_KEY_ACTION, "Action", "action")
    if economy.is_available(ActionType.BONUS_ACTION):
        _add(options, tags, _LEVEL1_KEY_BONUS, "Bonus Action", "bonus")
    if economy.is_available(ActionType.REACTION):
        _add(options, tags, _LEVEL1_KEY_REACTION, "Reaction", "reaction")
    inv = ctx.combatant.inventory
    if inv is not None and len(inv.slots) > 0:
        _add(options, tags, _LEVEL1_KEY_ITEM, "Item", "item")
    _add(options, tags, _LEVEL1_KEY_END_TURN, "End Turn", "end_turn")


def _build_level2(
    category: _Category | None, ctx: TurnContext,
    options: list[MenuOption], tags: dict[int, str],
) -> None:
    """Constroi opcoes do nivel 2 baseado na categoria."""
    builder = _LEVEL2_BUILDERS.get(category)
    if builder is not None:
        builder(ctx, options, tags)


def _build_action_options(
    ctx: TurnContext,
    options: list[MenuOption], tags: dict[int, str],
) -> None:
    _add(options, tags, 1, PlayerActionType.BASIC_ATTACK.label, "basic_attack")
    key = 2
    for skill in _skills_for_type(ctx, ActionType.ACTION):
        label = _skill_label(skill)
        available = _is_skill_available(skill, ctx)
        reason = _skill_unavailable_reason(skill, ctx)
        _add(options, tags, key, label, f"skill:{skill.skill_id}",
             available=available, reason=reason)
        key += 1


def _build_bonus_options(
    ctx: TurnContext,
    options: list[MenuOption], tags: dict[int, str],
) -> None:
    _add(options, tags, 1, "Move", "move")
    key = 2
    for skill in _skills_for_type(ctx, ActionType.BONUS_ACTION):
        label = _skill_label(skill)
        available = _is_skill_available(skill, ctx)
        reason = _skill_unavailable_reason(skill, ctx)
        _add(options, tags, key, label, f"skill:{skill.skill_id}",
             available=available, reason=reason)
        key += 1


def _build_reaction_options(
    ctx: TurnContext,
    options: list[MenuOption], tags: dict[int, str],
) -> None:
    _add(options, tags, 1, "Defend", "defend")
    key = 2
    for skill in _skills_for_type(ctx, ActionType.REACTION):
        label = _skill_label(skill)
        available = _is_skill_available(skill, ctx)
        reason = _skill_unavailable_reason(skill, ctx)
        _add(options, tags, key, label, f"skill:{skill.skill_id}",
             available=available, reason=reason)
        key += 1


def _skills_for_type(
    ctx: TurnContext,
    action_type: ActionType,
) -> list[Skill]:
    """Retorna skills do combatente filtradas por action_type."""
    bar = ctx.combatant.skill_bar
    if bar is None:
        return []
    return [s for s in bar.all_skills if s.action_type == action_type]


def _skill_label(skill: Skill) -> str:
    """Label da skill com custo de mana e/ou recurso."""
    parts = [skill.name]
    costs = []
    if skill.mana_cost > 0:
        costs.append(f"{skill.mana_cost} mana")
    for rc in skill.resource_costs:
        costs.append(f"{rc.amount} {_resource_display(rc.resource_type)}")
    if costs:
        parts.append(f"({', '.join(costs)})")
    return " ".join(parts)


_RESOURCE_NAMES: dict[str, str] = {
    "fury_bar": "Fury",
    "holy_power": "Holy",
    "action_points": "AP",
    "insanity_bar": "Insanity",
    "equilibrium_bar": "Eq",
    "groove": "Groove",
}


def _resource_display(resource_type: str) -> str:
    return _RESOURCE_NAMES.get(resource_type, resource_type)


def _build_item_options(
    ctx: TurnContext,
    options: list[MenuOption], tags: dict[int, str],
) -> None:
    inv = ctx.combatant.inventory
    if inv is None:
        return
    key = 1
    for slot in inv.slots:
        label = f"{slot.consumable.name} x{slot.quantity}"
        _add(options, tags, key, label, f"item:{slot.consumable.consumable_id}")
        key += 1


_ALLY_TARGET_TYPES = frozenset({
    TargetType.SINGLE_ALLY,
})


def _build_level3(
    ctx: TurnContext, target_type: TargetType,
    options: list[MenuOption], tags: dict[int, str],
) -> None:
    """Constroi opcoes do nivel 3: alvos vivos (allies ou enemies)."""
    if target_type in _ALLY_TARGET_TYPES:
        pool = [a for a in ctx.allies if a.is_alive]
    else:
        pool = [e for e in ctx.enemies if e.is_alive]
    key = 1
    for char in pool:
        _add(options, tags, key, char.name, char.name)
        key += 1


def _add(
    options: list[MenuOption], tags: dict[int, str],
    key: int, label: str, tag: str, *,
    available: bool = True, reason: str = "",
) -> None:
    options.append(MenuOption(
        key=key, label=label, available=available, reason=reason,
    ))
    tags[key] = tag


def _is_skill_available(skill: Skill, ctx: TurnContext) -> bool:
    bar = ctx.combatant.skill_bar
    if bar is None:
        return False
    if not bar.cooldown_tracker.is_ready(skill.skill_id):
        return False
    if skill.mana_cost > ctx.combatant.current_mana:
        return False
    if not _can_afford_all(ctx.combatant, skill):
        return False
    return True


def _can_afford_all(combatant: object, skill: Skill) -> bool:
    return all(
        can_afford_resource(combatant, cost)
        for cost in skill.resource_costs
    )


def _skill_unavailable_reason(skill: Skill, ctx: TurnContext) -> str:
    bar = ctx.combatant.skill_bar
    if bar is not None and not bar.cooldown_tracker.is_ready(skill.skill_id):
        remaining = bar.cooldown_tracker.remaining(skill.skill_id)
        return f"CD: {remaining}"
    if skill.mana_cost > ctx.combatant.current_mana:
        return "No mana"
    for cost in skill.resource_costs:
        if not can_afford_resource(ctx.combatant, cost):
            name = _resource_display(cost.resource_type)
            return f"No {name} ({cost.amount})"
    return ""


def _find_skill(skill_id: str, ctx: TurnContext) -> Skill | None:
    bar = ctx.combatant.skill_bar
    if bar is None:
        return None
    return next(
        (s for s in bar.all_skills if s.skill_id == skill_id), None,
    )


_LEVEL2_BUILDERS = {
    _Category.ACTION: _build_action_options,
    _Category.BONUS: _build_bonus_options,
    _Category.REACTION: _build_reaction_options,
    _Category.ITEM: _build_item_options,
}
