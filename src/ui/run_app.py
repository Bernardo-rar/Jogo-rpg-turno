"""RunApp — entry point do roguelite, conecta tudo."""

from __future__ import annotations

from random import Random

import pygame

from src.core.combat.skill_effect_applier import set_run_modifier_effect
from src.core.progression.level_up_system import LevelUpSystem
from src.core.progression.xp_reward_config import load_xp_reward_config
from src.core.progression.xp_table import load_xp_table
from src.core.progression.attribute_point_config import load_attribute_points
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.run.run_orchestrator import RunOrchestrator, SceneRequest
from src.dungeon.run.run_state import RunState
from src.ui.catalog_loader import load_app_catalogs, AppCatalogs
from src.ui.combat_reward_handler import (
    CombatContext,
    CombatRewardHandler,
)
from src.ui.font_manager import FontManager
from src.ui.game import Game
from src.ui.scene_builders import SceneContext
from src.ui.scenes.fade_transition import FadeTransition
from src.ui import scene_builders as sb

_ROOM_COMPLETE_SCENES = frozenset({
    SceneRequest.REST_ROOM,
    SceneRequest.TREASURE_ROOM,
    SceneRequest.EVENT_ROOM,
    SceneRequest.CAMPFIRE_ROOM,
    SceneRequest.SHOP_ROOM,
})


class RunApp:
    """Orquestra o loop completo do roguelite."""

    def __init__(self) -> None:
        self._fonts: FontManager | None = None
        self._game: Game | None = None
        self._orchestrator = RunOrchestrator()
        self._state: RunState | None = None
        self._catalogs: AppCatalogs | None = None
        self._combat_ctx = CombatContext()
        self._reward_handler = CombatRewardHandler(
            load_xp_reward_config(),
        )
        self._level_system: LevelUpSystem | None = None

    def start(self) -> None:
        """Inicializa Pygame e inicia o game loop."""
        pygame.init()
        self._catalogs = load_app_catalogs()
        self._fonts = FontManager()
        menu = sb.build_main_menu(
            self._fonts, self._on_scene_complete,
        )
        self._game = Game(menu)
        self._game.run()

    def _on_scene_complete(
        self,
        scene_id: SceneRequest,
        result: dict,
    ) -> None:
        """Callback chamado quando uma cena termina."""
        self._handle_side_effects(scene_id, result)
        transition = self._orchestrator.on_scene_complete(
            scene_id, result,
        )
        next_scene = self._build_scene(
            transition.target, transition.data,
        )
        if next_scene is not None and self._game is not None:
            self._transition_to(next_scene)

    def _handle_side_effects(
        self,
        scene_id: SceneRequest,
        result: dict,
    ) -> None:
        """Processa efeitos colaterais da cena completada."""
        if self._state is None:
            return
        if scene_id == SceneRequest.COMBAT:
            self._reward_handler.handle_post_combat(
                result, self._state, self._combat_ctx,
                self._level_system,
                self._catalogs.consumables,
            )
        elif scene_id in _ROOM_COMPLETE_SCENES:
            self._reward_handler.handle_post_room(
                self._state, self._combat_ctx.node_id,
                self._catalogs.consumables,
            )

    def _transition_to(self, next_scene: object) -> None:
        """Troca de cena com fade out/in."""
        old = self._game.current_scene
        fade = FadeTransition(
            old_scene=old, new_scene=next_scene,
            on_done=lambda: self._game.set_scene(next_scene),
        )
        self._game.set_scene(fade)

    def _build_scene(self, target: SceneRequest, data: dict) -> object:
        """Despacha para o builder correto."""
        builder = _SCENE_DISPATCH.get(target)
        if builder is None:
            return sb.build_main_menu(
                self._fonts, self._on_scene_complete,
            )
        return builder(self, data)

    def _scene_ctx(self) -> SceneContext:
        """Cria SceneContext com estado atual."""
        return SceneContext(
            fonts=self._fonts,
            state=self._state,
            combat_ctx=self._combat_ctx,
            on_complete=self._on_scene_complete,
        )

    def _create_run_state(self, result: dict, pf: object) -> None:
        """Cria RunState apos party select."""
        class_ids = result["class_ids"]
        party = [
            pf.create(cid, cid.value.capitalize())
            for cid in class_ids
        ]
        seed = Random().randint(0, 999999)
        floor_map = MapGenerator().generate(seed)
        self._state = RunState(
            seed=seed, party=party, floor_map=floor_map,
        )
        self._level_system = LevelUpSystem(
            load_xp_table(), load_attribute_points(),
        )

    def _apply_modifiers(self, modifiers: list) -> None:
        """Armazena modifiers e configura efeito global."""
        if self._state is None:
            return
        self._state.active_modifiers = list(modifiers)
        set_run_modifier_effect(self._state.aggregated_effects)


# ---------------------------------------------------------------------------
# Dispatch: SceneRequest -> builder(app, data) -> Scene
# ---------------------------------------------------------------------------

def _b_main_menu(app: RunApp, _: dict) -> object:
    return sb.build_main_menu(
        app._fonts, app._on_scene_complete,
    )


def _b_party_select(app: RunApp, _: dict) -> object:
    return sb.build_party_select(
        app._scene_ctx(),
        app._catalogs.party_factory,
        app._create_run_state,
    )


def _b_modifier(app: RunApp, _: dict) -> object:
    return sb.build_modifier_select(
        app._scene_ctx(), app._apply_modifiers,
    )


def _b_dungeon_map(app: RunApp, _: dict) -> object:
    return sb.build_dungeon_map(app._scene_ctx())


def _b_combat(app: RunApp, data: dict) -> object:
    return sb.build_combat(
        data, app._scene_ctx(),
        app._catalogs.encounter_builder,
    )


def _b_combat_reward(app: RunApp, data: dict) -> object:
    return sb.build_combat_reward(
        data, app._scene_ctx(),
        app._reward_handler.last_reward,
    )


def _b_rest_room(app: RunApp, data: dict) -> object:
    return sb.build_rest_room(data, app._scene_ctx())


def _b_treasure(app: RunApp, data: dict) -> object:
    return sb.build_treasure(data, app._scene_ctx())


def _b_event(app: RunApp, data: dict) -> object:
    return sb.build_event(data, app._scene_ctx())


def _b_campfire(app: RunApp, data: dict) -> object:
    return sb.build_campfire(data, app._scene_ctx())


def _b_shop(app: RunApp, data: dict) -> object:
    return sb.build_shop(data, app._scene_ctx())


def _b_equipment(app: RunApp, _: dict) -> object:
    return sb.build_equipment(
        app._scene_ctx(), app._catalogs.equipment,
    )


def _b_item_use(app: RunApp, _: dict) -> object:
    return sb.build_item_use(app._scene_ctx())


def _b_level_up(app: RunApp, data: dict) -> object:
    return sb.build_level_up(
        data, app._scene_ctx(),
        app._reward_handler.last_reward,
        app._level_system,
    )


def _b_loadout(app: RunApp, _: dict) -> object:
    return sb.build_loadout(app._scene_ctx())


def _b_subclass(app: RunApp, data: dict) -> object:
    return sb.build_subclass_choice(data, app._scene_ctx())


def _b_talent(app: RunApp, data: dict) -> object:
    return sb.build_talent_choice(data, app._scene_ctx())


def _b_game_over(app: RunApp, _: dict) -> object:
    return sb.build_game_over(
        app._fonts, app._state, app._on_scene_complete,
    )


def _b_victory(app: RunApp, _: dict) -> object:
    return sb.build_victory(
        app._fonts, app._state, app._on_scene_complete,
    )


_SCENE_DISPATCH: dict[SceneRequest, object] = {
    SceneRequest.MAIN_MENU: _b_main_menu,
    SceneRequest.PARTY_SELECT: _b_party_select,
    SceneRequest.MODIFIER_SELECT: _b_modifier,
    SceneRequest.DUNGEON_MAP: _b_dungeon_map,
    SceneRequest.COMBAT: _b_combat,
    SceneRequest.COMBAT_REWARD: _b_combat_reward,
    SceneRequest.REST_ROOM: _b_rest_room,
    SceneRequest.TREASURE_ROOM: _b_treasure,
    SceneRequest.EVENT_ROOM: _b_event,
    SceneRequest.CAMPFIRE_ROOM: _b_campfire,
    SceneRequest.SHOP_ROOM: _b_shop,
    SceneRequest.EQUIPMENT: _b_equipment,
    SceneRequest.ITEM_USE: _b_item_use,
    SceneRequest.LEVEL_UP: _b_level_up,
    SceneRequest.LOADOUT: _b_loadout,
    SceneRequest.SUBCLASS_CHOICE: _b_subclass,
    SceneRequest.TALENT_CHOICE: _b_talent,
    SceneRequest.GAME_OVER: _b_game_over,
    SceneRequest.VICTORY: _b_victory,
}
