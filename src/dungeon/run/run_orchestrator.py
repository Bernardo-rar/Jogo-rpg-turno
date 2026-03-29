"""RunOrchestrator — roteamento de cenas do roguelite."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from src.dungeon.map.room_type import RoomType


class SceneRequest(Enum):
    """Identificador de cada cena do jogo."""

    MAIN_MENU = auto()
    PARTY_SELECT = auto()
    MODIFIER_SELECT = auto()
    DUNGEON_MAP = auto()
    COMBAT = auto()
    REST_ROOM = auto()
    COMBAT_REWARD = auto()
    TREASURE_ROOM = auto()
    EVENT_ROOM = auto()
    CAMPFIRE_ROOM = auto()
    SHOP_ROOM = auto()
    EQUIPMENT = auto()
    ITEM_USE = auto()
    LEVEL_UP = auto()
    LOADOUT = auto()
    SUBCLASS_CHOICE = auto()
    TALENT_CHOICE = auto()
    GAME_OVER = auto()
    VICTORY = auto()


@dataclass(frozen=True)
class SceneTransition:
    """Transição para próxima cena com dados contextuais."""

    target: SceneRequest
    data: dict[str, object] = field(default_factory=dict)


_ROOM_TO_SCENE: dict[RoomType, SceneRequest] = {
    RoomType.COMBAT: SceneRequest.COMBAT,
    RoomType.ELITE: SceneRequest.COMBAT,
    RoomType.BOSS: SceneRequest.COMBAT,
    RoomType.REST: SceneRequest.REST_ROOM,
    RoomType.TREASURE: SceneRequest.TREASURE_ROOM,
    RoomType.EVENT: SceneRequest.EVENT_ROOM,
    RoomType.CAMPFIRE: SceneRequest.CAMPFIRE_ROOM,
    RoomType.SHOP: SceneRequest.SHOP_ROOM,
}


class RunOrchestrator:
    """Decide qual cena vem depois com base no estado da run."""

    def on_scene_complete(
        self,
        completed: SceneRequest,
        result: dict[str, object],
    ) -> SceneTransition:
        """Retorna a próxima cena baseado na cena completada."""
        handler = _DISPATCH.get(completed, _default_transition)
        return handler(result)


def _on_main_menu(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.PARTY_SELECT)


def _on_party_select(result: dict) -> SceneTransition:
    return SceneTransition(
        target=SceneRequest.MODIFIER_SELECT,
        data=result,
    )


def _on_modifier_select(result: dict) -> SceneTransition:
    return SceneTransition(
        target=SceneRequest.DUNGEON_MAP,
        data=result,
    )


def _on_dungeon_map(result: dict) -> SceneTransition:
    if result.get("equipment"):
        return SceneTransition(target=SceneRequest.EQUIPMENT, data=result)
    if result.get("item_use"):
        return SceneTransition(target=SceneRequest.ITEM_USE, data=result)
    if result.get("loadout"):
        return SceneTransition(target=SceneRequest.LOADOUT, data=result)
    room_type = result.get("room_type")
    if not isinstance(room_type, RoomType):
        return SceneTransition(target=SceneRequest.DUNGEON_MAP)
    target = _ROOM_TO_SCENE.get(room_type, SceneRequest.COMBAT)
    return SceneTransition(target=target, data=result)


def _on_combat(result: dict) -> SceneTransition:
    victory = result.get("victory", False)
    party_alive = result.get("party_alive", True)
    if not party_alive:
        return SceneTransition(target=SceneRequest.GAME_OVER, data=result)
    if victory:
        return SceneTransition(target=SceneRequest.COMBAT_REWARD, data=result)
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_combat_reward(result: dict) -> SceneTransition:
    has_points = result.get("has_points", False)
    if has_points:
        return SceneTransition(target=SceneRequest.LEVEL_UP, data=result)
    return _check_subclass(result)


def _on_level_up(result: dict) -> SceneTransition:
    return _check_subclass(result)


def _check_subclass(result: dict) -> SceneTransition:
    new_level = result.get("new_level", 0)
    if new_level == 3:
        return SceneTransition(target=SceneRequest.SUBCLASS_CHOICE, data=result)
    return _check_talent(result)


def _on_subclass_choice(result: dict) -> SceneTransition:
    return _check_talent(result)


def _check_talent(result: dict) -> SceneTransition:
    new_level = result.get("new_level", 0)
    if new_level in (5, 7, 9):
        return SceneTransition(target=SceneRequest.TALENT_CHOICE, data=result)
    return _after_all_choices(result)


def _on_talent_choice(result: dict) -> SceneTransition:
    return _after_all_choices(result)


def _after_all_choices(result: dict) -> SceneTransition:
    is_boss = result.get("is_boss", False)
    if is_boss:
        return SceneTransition(target=SceneRequest.VICTORY, data=result)
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_rest_room(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_treasure_room(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_event_room(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_campfire_room(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_shop_room(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_equipment(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_item_use(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_loadout(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_end_screen(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.MAIN_MENU)


def _default_transition(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.MAIN_MENU)


_DISPATCH: dict[SceneRequest, object] = {
    SceneRequest.MAIN_MENU: _on_main_menu,
    SceneRequest.PARTY_SELECT: _on_party_select,
    SceneRequest.MODIFIER_SELECT: _on_modifier_select,
    SceneRequest.DUNGEON_MAP: _on_dungeon_map,
    SceneRequest.COMBAT: _on_combat,
    SceneRequest.COMBAT_REWARD: _on_combat_reward,
    SceneRequest.REST_ROOM: _on_rest_room,
    SceneRequest.TREASURE_ROOM: _on_treasure_room,
    SceneRequest.EVENT_ROOM: _on_event_room,
    SceneRequest.CAMPFIRE_ROOM: _on_campfire_room,
    SceneRequest.SHOP_ROOM: _on_shop_room,
    SceneRequest.EQUIPMENT: _on_equipment,
    SceneRequest.ITEM_USE: _on_item_use,
    SceneRequest.LEVEL_UP: _on_level_up,
    SceneRequest.LOADOUT: _on_loadout,
    SceneRequest.SUBCLASS_CHOICE: _on_subclass_choice,
    SceneRequest.TALENT_CHOICE: _on_talent_choice,
    SceneRequest.GAME_OVER: _on_end_screen,
    SceneRequest.VICTORY: _on_end_screen,
}
