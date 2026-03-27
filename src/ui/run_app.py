"""RunApp — entry point do roguelite, conecta tudo."""

from __future__ import annotations

import json
from random import Random

import pygame

from src.core._paths import resolve_data_path
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.composite_handler import CompositeHandler
from src.core.combat.skill_effect_applier import set_combo_detector
from src.core.combat.skill_handler import SkillHandler
from src.core.elements.combo.combo_config import load_combo_configs
from src.core.elements.combo.combo_detector import ComboDetector
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile, load_profiles
from src.core.items.weapon import Weapon
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_skills
from src.dungeon.encounters.encounter_factory import EncounterFactory
from src.dungeon.enemies.bosses.boss_factory import BossFactory
from src.dungeon.enemies.elite_modifier import load_elite_bonuses
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.map.room_type import RoomType
from src.dungeon.economy.gold_reward import CombatInfo
from src.dungeon.run.combat_bridge import (
    CombatRewardContext,
    after_combat,
    prepare_for_combat,
)
from src.dungeon.run.encounter_builder import EncounterBuilder
from src.dungeon.run.run_orchestrator import RunOrchestrator, SceneRequest
from src.dungeon.run.run_state import RunState
from src.dungeon.run.party_factory import PartyFactory
from src.ui.font_manager import FontManager
from src.ui.game import Game
from src.ui.scenes.dungeon_map_scene import DungeonMapScene
from src.ui.scenes.game_over_scene import GameOverScene
from src.ui.scenes.interactive_combat_factory import create_interactive_combat
from src.ui.scenes.main_menu_scene import MainMenuScene
from src.ui.scenes.party_select_scene import PartySelectScene
from src.ui.scenes.playable_combat_scene import PlayableCombatScene
from src.ui.scenes.rest_room_scene import RestRoomScene
from src.ui.scenes.fade_transition import FadeTransition
from src.ui.scenes.victory_scene import VictoryScene

_DEFAULT_SEED = 42


class RunApp:
    """Orquestra o loop completo do roguelite."""

    def __init__(self) -> None:
        self._fonts: FontManager | None = None
        self._game: Game | None = None
        self._orchestrator = RunOrchestrator()
        self._state: RunState | None = None
        self._encounter_builder: EncounterBuilder | None = None
        self._party_factory: PartyFactory | None = None
        self._combat_node_id: str | None = None
        self._combat_is_boss: bool = False
        self._combat_is_elite: bool = False
        self._combat_enemy_count: int = 0

    def start(self) -> None:
        """Inicializa Pygame e inicia o game loop."""
        pygame.init()
        self._load_catalogs()
        self._fonts = FontManager()
        menu = self._build_main_menu()
        self._game = Game(menu)
        self._game.run()

    def _load_catalogs(self) -> None:
        weapons = load_weapons()
        self._party_factory = PartyFactory(weapons)
        enc_factory = _build_encounter_factory()
        boss_factory = _build_boss_factory()
        self._encounter_builder = EncounterBuilder(enc_factory, boss_factory)
        _init_combo_detector()

    def _on_scene_complete(
        self,
        scene_id: SceneRequest,
        result: dict,
    ) -> None:
        """Callback chamado quando uma cena termina."""
        if scene_id == SceneRequest.COMBAT:
            self._handle_post_combat(result)
        elif scene_id == SceneRequest.REST_ROOM:
            self._handle_post_rest(result)
        transition = self._orchestrator.on_scene_complete(scene_id, result)
        next_scene = self._build_scene(transition.target, transition.data)
        if next_scene is not None and self._game is not None:
            self._transition_to(next_scene)

    def _handle_post_combat(self, result: dict) -> None:
        if self._state is None:
            return
        result["is_boss"] = self._combat_is_boss
        result["party_alive"] = self._state.is_party_alive
        if self._combat_node_id:
            ctx = self._build_reward_context()
            after_combat(self._state, self._combat_node_id, ctx)

    def _build_reward_context(self) -> CombatRewardContext:
        """Cria contexto de recompensa para o combate atual."""
        info = CombatInfo(
            enemy_count=self._combat_enemy_count,
            tier=1,
            is_elite=self._combat_is_elite,
            is_boss=self._combat_is_boss,
        )
        rng = Random(self._state.seed + hash(self._combat_node_id))
        return CombatRewardContext(info=info, rng=rng)

    def _handle_post_rest(self, result: dict) -> None:
        if self._state is None or self._combat_node_id is None:
            return
        after_combat(self._state, self._combat_node_id)

    def _transition_to(self, next_scene: object) -> None:
        """Troca de cena com fade out/in."""
        old_scene = self._game.current_scene
        fade = FadeTransition(
            old_scene=old_scene,
            new_scene=next_scene,
            on_done=lambda: self._game.set_scene(next_scene),
        )
        self._game.set_scene(fade)

    def _build_scene(self, target: SceneRequest, data: dict) -> object:
        builders = {
            SceneRequest.MAIN_MENU: self._build_main_menu,
            SceneRequest.PARTY_SELECT: self._build_party_select,
            SceneRequest.DUNGEON_MAP: self._build_dungeon_map,
            SceneRequest.COMBAT: lambda: self._build_combat(data),
            SceneRequest.REST_ROOM: lambda: self._build_rest_room(data),
            SceneRequest.GAME_OVER: self._build_game_over,
            SceneRequest.VICTORY: self._build_victory,
        }
        builder = builders.get(target, self._build_main_menu)
        return builder()

    def _build_main_menu(self) -> MainMenuScene:
        return MainMenuScene(
            self._fonts,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.MAIN_MENU, r,
            ),
        )

    def _build_party_select(self) -> PartySelectScene:
        def on_done(result: dict) -> None:
            class_ids = result["class_ids"]
            party = [
                self._party_factory.create(cid, cid.value.capitalize())
                for cid in class_ids
            ]
            seed = Random().randint(0, 999999)
            floor_map = MapGenerator().generate(seed)
            self._state = RunState(
                seed=seed, party=party, floor_map=floor_map,
            )
            self._on_scene_complete(
                SceneRequest.PARTY_SELECT, result,
            )

        return PartySelectScene(self._fonts, on_complete=on_done)

    def _build_dungeon_map(self) -> DungeonMapScene:
        def on_node_selected(result: dict) -> None:
            self._combat_node_id = result.get("node_id")
            room_type = result.get("room_type")
            self._combat_is_boss = room_type == RoomType.BOSS
            self._combat_is_elite = room_type == RoomType.ELITE
            self._on_scene_complete(SceneRequest.DUNGEON_MAP, result)

        return DungeonMapScene(
            self._fonts,
            self._state.floor_map,
            self._state.current_node_id,
            on_complete=on_node_selected,
        )

    def _build_combat(self, data: dict) -> PlayableCombatScene:
        node_id = data.get("node_id", "")
        node = self._state.floor_map.get_node(node_id)
        rng = Random(self._state.seed + hash(node_id))
        setup = self._encounter_builder.build(node, rng)
        self._combat_enemy_count = len(setup.enemies)
        alive_party = self._state.alive_members
        prepare_for_combat(alive_party)
        ai_handler = setup.handler
        interactive = create_interactive_combat(
            alive_party, setup.enemies, ai_handler,
        )
        return PlayableCombatScene(
            interactive, alive_party, setup.enemies, self._fonts,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.COMBAT, r,
            ),
        )

    def _build_rest_room(self, data: dict) -> RestRoomScene:
        self._combat_node_id = data.get("node_id")
        return RestRoomScene(
            self._fonts,
            self._state.party,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.REST_ROOM, r,
            ),
        )

    def _build_game_over(self) -> GameOverScene:
        rooms = self._state.rooms_cleared if self._state else 0
        return GameOverScene(
            self._fonts, rooms,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.GAME_OVER, r,
            ),
        )

    def _build_victory(self) -> VictoryScene:
        rooms = self._state.rooms_cleared if self._state else 0
        return VictoryScene(
            self._fonts, rooms,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.VICTORY, r,
            ),
        )


def _load_dungeon_catalogs(
    extra_skill_files: list[str],
) -> tuple[dict[str, Weapon], dict[str, ElementalProfile], dict[str, Skill]]:
    """Load weapons, profiles, and skills shared by encounter/boss factories."""
    core_weapons = load_weapons()
    raw_dw = json.loads(
        resolve_data_path("data/dungeon/enemies/weapons.json")
        .read_text(encoding="utf-8"),
    )
    dungeon_weapons = {k: Weapon.from_dict(v) for k, v in raw_dw.items()}
    core_profiles = load_profiles()
    raw_dp = json.loads(
        resolve_data_path("data/dungeon/enemies/elemental_profiles.json")
        .read_text(encoding="utf-8"),
    )
    dungeon_profiles = {
        name: ElementalProfile(
            resistances={ElementType[k]: v for k, v in r.items()},
        )
        for name, r in raw_dp.items()
    }
    core_skills = load_skills()
    extra: dict[str, Skill] = {}
    for path in extra_skill_files:
        raw = json.loads(
            resolve_data_path(path).read_text(encoding="utf-8"),
        )
        extra.update(
            {sid: Skill.from_dict(sid, data) for sid, data in raw.items()},
        )
    weapons = {**core_weapons, **dungeon_weapons}
    profiles = {**core_profiles, **dungeon_profiles}
    skills = {**core_skills, **extra}
    return weapons, profiles, skills


def _build_encounter_factory() -> EncounterFactory:
    weapons, profiles, skills = _load_dungeon_catalogs([
        "data/dungeon/enemies/skills/tier1_skills.json",
        "data/dungeon/enemies/skills/elite_skills.json",
    ])
    enemy_factory = EnemyFactory(weapons, profiles, skills)
    elite_bonuses = load_elite_bonuses()
    return EncounterFactory(
        enemy_factory, load_tier_templates(tier=1),
        elite_bonuses=elite_bonuses,
    )


def _build_boss_factory() -> BossFactory:
    weapons, profiles, skills = _load_dungeon_catalogs([
        "data/dungeon/enemies/skills/boss_skills.json",
    ])
    return BossFactory(weapons, profiles, skills)


def _init_combo_detector() -> None:
    """Carrega combos elementais e configura o detector global."""
    combos = load_combo_configs()
    detector = ComboDetector(combos=combos)
    set_combo_detector(detector)
