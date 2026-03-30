"""Scene builder functions — cada funcao constroi uma cena do jogo."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import TYPE_CHECKING, Callable

from src.core.combat.skill_effect_applier import set_run_modifier_effect
from src.core.progression.subclass_applier import apply_subclass
from src.core.progression.subclass_config import load_subclass_registry
from src.core.progression.talent_applier import apply_talent
from src.core.progression.talent_config import load_talents
from src.core.progression.talent_picker import generate_talent_offering
from src.dungeon.map.room_type import RoomType
from src.dungeon.modifiers.modifier_loader import load_modifiers
from src.dungeon.run.combat_bridge import prepare_for_combat
from src.dungeon.run.run_orchestrator import SceneRequest
from src.dungeon.run.run_state import RunState
from src.dungeon.run.treasure_actions import resolve_treasure
from src.dungeon.events.event_loader import load_events
from src.dungeon.run.event_actions import apply_event_choice
from src.dungeon.run.campfire_actions import (
    load_campfire_buffs,
    apply_campfire_buff,
)
from src.dungeon.shop.shop_loader import load_shop
from src.ui.scenes.main_menu_scene import MainMenuScene
from src.ui.scenes.party_select_scene import PartySelectScene
from src.ui.scenes.modifier_select_scene import ModifierSelectScene
from src.ui.scenes.dungeon_map_scene import DungeonMapScene
from src.ui.scenes.playable_combat_scene import PlayableCombatScene
from src.ui.scenes.interactive_combat_factory import (
    create_interactive_combat,
)
from src.ui.scenes.rest_room_scene import RestRoomScene
from src.ui.scenes.combat_reward_scene import CombatRewardScene, RewardSceneConfig
from src.ui.scenes.treasure_scene import TreasureScene
from src.ui.scenes.event_scene import EventScene
from src.ui.scenes.campfire_scene import CampfireScene
from src.ui.scenes.shop_scene import ShopCallbacks, ShopScene
from src.ui.scenes.equipment_scene import EquipmentConfig, EquipmentScene
from src.ui.scenes.item_use_scene import ItemUseScene
from src.ui.scenes.level_up_scene import LevelUpConfig, LevelUpScene
from src.ui.scenes.loadout_scene import LoadoutScene
from src.ui.scenes.subclass_choice_scene import SubclassChoiceScene
from src.ui.scenes.talent_choice_scene import TalentChoiceScene
from src.ui.scenes.game_over_scene import GameOverScene
from src.ui.scenes.victory_scene import VictoryScene

if TYPE_CHECKING:
    from src.core.progression.level_up_system import LevelUpSystem
    from src.dungeon.run.combat_bridge import CombatRewardResult
    from src.dungeon.run.encounter_builder import EncounterBuilder
    from src.dungeon.run.equipment_catalog import EquipmentCatalogs
    from src.dungeon.run.party_factory import PartyFactory
    from src.ui.combat_reward_handler import CombatContext
    from src.ui.font_manager import FontManager

# Tipo do callback padrao de cena
SceneCallback = Callable[[SceneRequest, dict], None]


@dataclass
class SceneContext:
    """Agrupa estado necessario para builders de cena."""

    fonts: FontManager
    state: RunState
    combat_ctx: CombatContext
    on_complete: SceneCallback


# ---------------------------------------------------------------------------
# Menu / Setup scenes
# ---------------------------------------------------------------------------

def build_main_menu(
    fonts: FontManager,
    on_complete: SceneCallback,
) -> MainMenuScene:
    set_run_modifier_effect(None)
    return MainMenuScene(
        fonts,
        on_complete=lambda r: on_complete(
            SceneRequest.MAIN_MENU, r,
        ),
    )


def build_party_select(
    ctx: SceneContext,
    party_factory: PartyFactory,
    on_state_created: Callable,
) -> PartySelectScene:
    def on_done(result: dict) -> None:
        on_state_created(result, party_factory)
        ctx.on_complete(SceneRequest.PARTY_SELECT, result)

    return PartySelectScene(ctx.fonts, on_complete=on_done)


def build_modifier_select(
    ctx: SceneContext,
    apply_modifiers: Callable,
) -> ModifierSelectScene:
    all_mods = list(load_modifiers().values())
    rng = Random(ctx.state.seed)
    offered = rng.sample(all_mods, min(3, len(all_mods)))

    def on_done(result: dict) -> None:
        apply_modifiers(result.get("modifiers", []))
        ctx.on_complete(SceneRequest.MODIFIER_SELECT, result)

    return ModifierSelectScene(ctx.fonts, offered, on_done)


# ---------------------------------------------------------------------------
# Map / Navigation scenes
# ---------------------------------------------------------------------------

def build_dungeon_map(ctx: SceneContext) -> DungeonMapScene:
    def on_node_selected(result: dict) -> None:
        ctx.combat_ctx.node_id = result.get("node_id")
        room_type = result.get("room_type")
        ctx.combat_ctx.is_boss = room_type == RoomType.BOSS
        ctx.combat_ctx.is_elite = room_type == RoomType.ELITE
        ctx.on_complete(SceneRequest.DUNGEON_MAP, result)

    return DungeonMapScene(
        ctx.fonts,
        ctx.state.floor_map,
        ctx.state.current_node_id,
        on_complete=on_node_selected,
    )


# ---------------------------------------------------------------------------
# Combat scenes
# ---------------------------------------------------------------------------

def build_combat(
    data: dict,
    ctx: SceneContext,
    encounter_builder: EncounterBuilder,
) -> PlayableCombatScene:
    node_id = data.get("node_id", "")
    node = ctx.state.floor_map.get_node(node_id)
    rng = Random(ctx.state.seed + hash(node_id))
    setup = encounter_builder.build(node, rng)
    ctx.combat_ctx.enemy_count = len(setup.enemies)
    alive = ctx.state.alive_members
    prepare_for_combat(alive)
    interactive = create_interactive_combat(
        alive, setup.enemies, setup.handler,
    )
    return PlayableCombatScene(
        interactive, alive, setup.enemies, ctx.fonts,
        on_complete=lambda r: ctx.on_complete(
            SceneRequest.COMBAT, r,
        ),
    )


def build_combat_reward(
    data: dict,
    ctx: SceneContext,
    last_reward: CombatRewardResult | None,
) -> CombatRewardScene:
    vals = _extract_reward_values(last_reward)
    is_boss = data.get("is_boss", False)
    from src.ui.combat_reward_handler import check_level_points
    has_pts = check_level_points(last_reward)

    def on_done(result: dict) -> None:
        result["is_boss"] = is_boss
        result["has_points"] = has_pts
        result["new_level"] = vals.new_level
        ctx.on_complete(SceneRequest.COMBAT_REWARD, result)

    cfg = RewardSceneConfig(
        gold_earned=vals.gold, drops=vals.drops,
        total_gold=ctx.state.gold, on_complete=on_done,
        xp_earned=vals.xp, leveled_up=vals.leveled,
        new_level=vals.new_level,
    )
    return CombatRewardScene(ctx.fonts, cfg)


@dataclass(frozen=True)
class _RewardValues:
    gold: int
    drops: tuple
    xp: int
    leveled: bool
    new_level: int


def _extract_reward_values(
    reward: CombatRewardResult | None,
) -> _RewardValues:
    """Extrai valores do reward ou retorna defaults."""
    if reward is None:
        return _RewardValues(0, (), 0, False, 0)
    return _RewardValues(
        gold=reward.gold_earned,
        drops=reward.drops,
        xp=reward.xp_earned,
        leveled=reward.leveled_up,
        new_level=reward.new_level,
    )


# ---------------------------------------------------------------------------
# Room scenes (rest, treasure, event, campfire, shop)
# ---------------------------------------------------------------------------

def build_rest_room(
    data: dict,
    ctx: SceneContext,
) -> RestRoomScene:
    ctx.combat_ctx.node_id = data.get("node_id")
    healing = ctx.state.aggregated_effects.healing_mult
    return RestRoomScene(
        ctx.fonts, ctx.state.party,
        on_complete=lambda r: ctx.on_complete(
            SceneRequest.REST_ROOM, r,
        ),
        healing_mult=healing,
    )


def build_treasure(data: dict, ctx: SceneContext) -> TreasureScene:
    node_id = data.get("node_id", "")
    ctx.combat_ctx.node_id = node_id
    rng = Random(ctx.state.seed + hash(node_id))
    result = resolve_treasure(ctx.state, rng)
    return TreasureScene(
        ctx.fonts, result,
        on_complete=lambda r: ctx.on_complete(
            SceneRequest.TREASURE_ROOM, r,
        ),
    )


def build_event(data: dict, ctx: SceneContext) -> EventScene:
    node_id = data.get("node_id", "")
    ctx.combat_ctx.node_id = node_id
    events = load_events()
    rng = Random(ctx.state.seed + hash(node_id))
    event_id = rng.choice(list(events.keys()))
    event = events[event_id]

    def on_choice(idx: int) -> dict[str, object]:
        return apply_event_choice(ctx.state, event.choices[idx])

    return EventScene(
        ctx.fonts, event, on_choice,
        on_complete=lambda r: ctx.on_complete(
            SceneRequest.EVENT_ROOM, r,
        ),
    )


def build_campfire(data: dict, ctx: SceneContext) -> CampfireScene:
    node_id = data.get("node_id", "")
    ctx.combat_ctx.node_id = node_id
    buffs = load_campfire_buffs()
    buff_list = list(buffs.values())

    def on_select(idx: int) -> dict[str, object]:
        return apply_campfire_buff(ctx.state, buff_list[idx])

    return CampfireScene(
        ctx.fonts, buff_list, on_select,
        on_complete=lambda r: ctx.on_complete(
            SceneRequest.CAMPFIRE_ROOM, r,
        ),
    )


def build_shop(data: dict, ctx: SceneContext) -> ShopScene:
    node_id = data.get("node_id", "")
    ctx.combat_ctx.node_id = node_id
    shop = load_shop(tier=1)
    cbs = ShopCallbacks(
        on_buy=lambda idx: shop.buy(idx, ctx.state),
        on_sell=lambda idx: shop.sell(idx, ctx.state),
        gold_getter=lambda: ctx.state.gold,
        loot_getter=lambda: ctx.state.pending_loot,
        on_complete=lambda r: ctx.on_complete(SceneRequest.SHOP_ROOM, r),
    )
    return ShopScene(ctx.fonts, shop, cbs)


# ---------------------------------------------------------------------------
# Equipment / Items / Loadout
# ---------------------------------------------------------------------------

def build_equipment(
    ctx: SceneContext,
    catalogs: EquipmentCatalogs,
) -> EquipmentScene:
    cfg = EquipmentConfig(
        party=ctx.state.party,
        equipment_stash=ctx.state.equipment_stash,
        catalogs=catalogs,
        on_complete=lambda r: ctx.on_complete(SceneRequest.EQUIPMENT, r),
        gold=ctx.state.gold,
    )
    return EquipmentScene(ctx.fonts, cfg)


def build_item_use(ctx: SceneContext) -> ItemUseScene:
    return ItemUseScene(
        ctx.fonts, ctx.state.party,
        on_complete=lambda r: ctx.on_complete(
            SceneRequest.ITEM_USE, r,
        ),
        gold=ctx.state.gold,
    )


def build_loadout(ctx: SceneContext) -> LoadoutScene:
    return LoadoutScene(
        ctx.fonts, ctx.state.party,
        on_complete=lambda r: ctx.on_complete(
            SceneRequest.LOADOUT, r,
        ),
    )


# ---------------------------------------------------------------------------
# Progression scenes (level up, subclass, talent)
# ---------------------------------------------------------------------------

def build_level_up(
    data: dict,
    ctx: SceneContext,
    last_reward: CombatRewardResult | None,
    level_system: LevelUpSystem | None,
) -> LevelUpScene:
    from src.core.progression.attribute_point_config import (
        get_points_for_level,
        load_attribute_points,
    )
    config = load_attribute_points()
    new_level = last_reward.new_level if last_reward else 0
    pts = get_points_for_level(new_level, config)
    is_boss = data.get("is_boss", False)

    def on_done(result: dict) -> None:
        result["is_boss"] = is_boss
        ctx.on_complete(SceneRequest.LEVEL_UP, result)

    cfg = LevelUpConfig(
        party=ctx.state.party,
        physical_points=pts.physical,
        mental_points=pts.mental,
        level_system=level_system,
        on_complete=on_done,
    )
    return LevelUpScene(ctx.fonts, cfg)


def build_subclass_choice(
    data: dict,
    ctx: SceneContext,
) -> SubclassChoiceScene:
    registry = load_subclass_registry()
    char_idx = data.get("_subclass_char_idx", 0)
    char = ctx.state.party[char_idx]
    class_id = type(char).__name__.lower()
    subclasses = registry.get(class_id)
    if subclasses is None:
        return _subclass_fallback(ctx, char, registry, data)
    is_boss = data.get("is_boss", False)
    on_done = _subclass_callback(
        char, char_idx, ctx, is_boss,
    )
    return SubclassChoiceScene(
        ctx.fonts, char, subclasses, on_complete=on_done,
    )


def _subclass_fallback(
    ctx: SceneContext,
    char: object,
    registry: dict,
    data: dict,
) -> SubclassChoiceScene:
    """Fallback quando classe nao tem subclasses."""
    ctx.on_complete(SceneRequest.SUBCLASS_CHOICE, data)
    return SubclassChoiceScene(
        ctx.fonts, char, registry["fighter"],
        on_complete=lambda r: None,
    )


def _subclass_callback(
    char: object,
    char_idx: int,
    ctx: SceneContext,
    is_boss: bool,
) -> Callable:
    """Cria callback de conclusao para subclass choice."""
    def on_done(result: dict) -> None:
        chosen = result.get("subclass")
        if chosen is not None:
            apply_subclass(char, chosen)
        result["is_boss"] = is_boss
        next_idx = char_idx + 1
        if next_idx < len(ctx.state.party):
            result["_subclass_char_idx"] = next_idx
            result["new_level"] = 3
        ctx.on_complete(SceneRequest.SUBCLASS_CHOICE, result)

    return on_done


def build_talent_choice(
    data: dict,
    ctx: SceneContext,
) -> TalentChoiceScene:
    all_talents = load_talents()
    char_idx = data.get("_talent_char_idx", 0)
    char = ctx.state.party[char_idx]
    class_id = type(char).__name__.lower()
    chosen_ids = data.get("_talent_chosen_ids", set())
    rng = Random(ctx.state.seed + char_idx + char.level)
    options = generate_talent_offering(
        class_id, all_talents, chosen_ids, rng,
    )
    is_boss = data.get("is_boss", False)
    new_level = data.get("new_level", 0)
    on_done = _talent_callback(
        char, char_idx, ctx, chosen_ids,
        is_boss, new_level,
    )
    return TalentChoiceScene(
        ctx.fonts, char, options, on_complete=on_done,
    )


@dataclass(frozen=True)
class _TalentCallbackArgs:
    """Argumentos para o callback de talent choice."""

    char: object
    char_idx: int
    chosen_ids: set
    is_boss: bool
    new_level: int


def _talent_callback(
    char: object,
    char_idx: int,
    ctx: SceneContext,
    chosen_ids: set,
    is_boss: bool,
    new_level: int,
) -> Callable:
    """Cria callback de conclusao para talent choice."""
    args = _TalentCallbackArgs(
        char, char_idx, chosen_ids, is_boss, new_level,
    )
    return _make_talent_on_done(args, ctx)


def _make_talent_on_done(
    args: _TalentCallbackArgs,
    ctx: SceneContext,
) -> Callable:
    """Constroi funcao on_done para talent callback."""
    def on_done(result: dict) -> None:
        talent = result.get("talent")
        if talent is not None:
            apply_talent(args.char, talent)
            args.chosen_ids.add(talent.talent_id)
        result["is_boss"] = args.is_boss
        result["new_level"] = args.new_level
        next_idx = args.char_idx + 1
        if next_idx < len(ctx.state.party):
            result["_talent_char_idx"] = next_idx
            result["_talent_chosen_ids"] = args.chosen_ids
        ctx.on_complete(SceneRequest.TALENT_CHOICE, result)

    return on_done


# ---------------------------------------------------------------------------
# End screens
# ---------------------------------------------------------------------------

def build_game_over(
    fonts: FontManager,
    state: RunState | None,
    on_complete: SceneCallback,
) -> GameOverScene:
    rooms = state.rooms_cleared if state else 0
    return GameOverScene(
        fonts, rooms,
        on_complete=lambda r: on_complete(
            SceneRequest.GAME_OVER, r,
        ),
    )


def build_victory(
    fonts: FontManager,
    state: RunState | None,
    on_complete: SceneCallback,
) -> VictoryScene:
    rooms = state.rooms_cleared if state else 0
    return VictoryScene(
        fonts, rooms,
        on_complete=lambda r: on_complete(
            SceneRequest.VICTORY, r,
        ),
    )
