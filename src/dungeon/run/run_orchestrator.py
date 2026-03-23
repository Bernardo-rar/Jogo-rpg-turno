"""RunOrchestrator — roteamento de cenas do roguelite."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from src.dungeon.map.room_type import RoomType


class SceneRequest(Enum):
    """Identificador de cada cena do jogo."""

    MAIN_MENU = auto()
    PARTY_SELECT = auto()
    DUNGEON_MAP = auto()
    COMBAT = auto()
    REST_ROOM = auto()
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
        target=SceneRequest.DUNGEON_MAP,
        data=result,
    )


def _on_dungeon_map(result: dict) -> SceneTransition:
    room_type = result.get("room_type")
    if not isinstance(room_type, RoomType):
        return SceneTransition(target=SceneRequest.DUNGEON_MAP)
    target = _ROOM_TO_SCENE.get(room_type, SceneRequest.COMBAT)
    return SceneTransition(target=target, data=result)


def _on_combat(result: dict) -> SceneTransition:
    victory = result.get("victory", False)
    is_boss = result.get("is_boss", False)
    party_alive = result.get("party_alive", True)
    if victory and is_boss:
        return SceneTransition(target=SceneRequest.VICTORY, data=result)
    if not party_alive:
        return SceneTransition(target=SceneRequest.GAME_OVER, data=result)
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_rest_room(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.DUNGEON_MAP, data=result)


def _on_end_screen(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.MAIN_MENU)


def _default_transition(result: dict) -> SceneTransition:
    return SceneTransition(target=SceneRequest.MAIN_MENU)


_DISPATCH: dict[SceneRequest, object] = {
    SceneRequest.MAIN_MENU: _on_main_menu,
    SceneRequest.PARTY_SELECT: _on_party_select,
    SceneRequest.DUNGEON_MAP: _on_dungeon_map,
    SceneRequest.COMBAT: _on_combat,
    SceneRequest.REST_ROOM: _on_rest_room,
    SceneRequest.GAME_OVER: _on_end_screen,
    SceneRequest.VICTORY: _on_end_screen,
}
