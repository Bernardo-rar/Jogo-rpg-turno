"""RunApp — entry point do roguelite, conecta tudo."""

from __future__ import annotations

import json
from random import Random

import pygame

from src.core._paths import resolve_data_path
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.composite_handler import CompositeHandler
from src.core.combat.skill_effect_applier import set_combo_detector, set_run_modifier_effect
from src.core.combat.skill_handler import SkillHandler
from src.core.elements.combo.combo_config import load_combo_configs
from src.core.elements.combo.combo_detector import ComboDetector
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile, load_profiles
from src.core.items.accessory_loader import load_accessories
from src.core.items.armor_loader import load_armors
from src.core.items.weapon import Weapon
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_skills
from src.dungeon.modifiers.modifier_loader import load_modifiers
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
    CombatRewardResult,
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
from src.ui.scenes.modifier_select_scene import ModifierSelectScene
from src.ui.scenes.rest_room_scene import RestRoomScene
from src.ui.scenes.fade_transition import FadeTransition
from src.ui.scenes.combat_reward_scene import CombatRewardScene
from src.ui.scenes.treasure_scene import TreasureScene
from src.ui.scenes.event_scene import EventScene
from src.ui.scenes.campfire_scene import CampfireScene
from src.ui.scenes.shop_scene import ShopScene
from src.ui.scenes.equipment_scene import EquipmentScene
from src.ui.scenes.item_use_scene import ItemUseScene
from src.ui.scenes.level_up_scene import LevelUpScene
from src.ui.scenes.loadout_scene import LoadoutScene
from src.ui.scenes.subclass_choice_scene import SubclassChoiceScene
from src.core.progression.subclass_config import load_subclass_registry
from src.core.progression.subclass_applier import apply_subclass
from src.core.progression.talent_config import load_talents
from src.core.progression.talent_picker import generate_talent_offering
from src.core.progression.talent_applier import apply_talent
from src.ui.scenes.talent_choice_scene import TalentChoiceScene
from src.ui.scenes.victory_scene import VictoryScene
from src.dungeon.run.equipment_catalog import EquipmentCatalogs
from src.dungeon.run.treasure_actions import resolve_treasure
from src.dungeon.events.event_loader import load_events
from src.dungeon.run.event_actions import apply_event_choice
from src.dungeon.run.campfire_actions import load_campfire_buffs, apply_campfire_buff
from src.dungeon.shop.shop_loader import load_shop
from src.dungeon.run.combat_bridge import mark_node_visited
from src.dungeon.run.loot_distributor import distribute_consumables
from src.core.items.consumable_loader import load_consumables
from src.core.progression.level_up_system import LevelUpSystem
from src.core.progression.xp_table import load_xp_table
from src.core.progression.attribute_point_config import load_attribute_points
from src.core.progression.xp_calculator import CombatXpInput, calculate_combat_xp
from src.core.progression.xp_reward_config import load_xp_reward_config

_DEFAULT_SEED = 42

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
        self._encounter_builder: EncounterBuilder | None = None
        self._party_factory: PartyFactory | None = None
        self._equipment_catalogs: EquipmentCatalogs | None = None
        self._combat_node_id: str | None = None
        self._combat_is_boss: bool = False
        self._combat_is_elite: bool = False
        self._combat_enemy_count: int = 0
        self._combat_rounds: int = 0
        self._combat_deaths: int = 0
        self._last_reward: CombatRewardResult | None = None
        self._level_system: LevelUpSystem | None = None
        self._xp_config = load_xp_reward_config()

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
        armors = load_armors()
        accessories = load_accessories()
        self._consumable_catalog = load_consumables()
        self._party_factory = PartyFactory(weapons, armors, accessories)
        self._equipment_catalogs = EquipmentCatalogs(
            weapons=weapons, armors=armors, accessories=accessories,
        )
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
        elif scene_id in _ROOM_COMPLETE_SCENES:
            self._handle_post_room(result)
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
            reward = after_combat(
                self._state, self._combat_node_id, ctx,
            )
            xp_result = self._grant_combat_xp(result)
            if reward is not None and xp_result is not None:
                reward = CombatRewardResult(
                    gold_earned=reward.gold_earned,
                    drops=reward.drops,
                    xp_earned=xp_result[0],
                    leveled_up=xp_result[1],
                    new_level=xp_result[2],
                )
            self._last_reward = reward
            self._collect_consumables()

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

    def _handle_post_room(self, result: dict) -> None:
        """Marca no como visitado apos completar sala nao-combate."""
        if self._state is None or self._combat_node_id is None:
            return
        mark_node_visited(self._state, self._combat_node_id)
        self._collect_consumables()

    def _grant_combat_xp(
        self, result: dict,
    ) -> tuple[int, bool, int] | None:
        """Calcula e aplica XP do combate. Retorna (xp, leveled, level)."""
        if self._level_system is None or self._state is None:
            return None
        if not result.get("victory", False):
            return None
        enc_type = self._encounter_type()
        combat_input = CombatXpInput(
            encounter_type=enc_type,
            tier=1,
            rounds=result.get("rounds", 10),
            party_deaths=result.get("deaths", 0),
            xp_run_mult=self._state.aggregated_effects.xp_mult,
        )
        xp = calculate_combat_xp(combat_input, self._xp_config)
        level_result = self._level_system.gain_party_xp(
            self._state.party, xp,
        )
        leveled = level_result is not None
        new_level = level_result.new_level if leveled else 0
        return (xp, leveled, new_level)

    def _encounter_type(self) -> str:
        """Retorna tipo de encontro para calculo de XP."""
        if self._combat_is_boss:
            return "boss"
        if self._combat_is_elite:
            return "elite"
        return "normal"

    def _collect_consumables(self) -> None:
        """Move consumiveis do pending_loot pro inventario da party."""
        if self._state is None:
            return
        remaining = distribute_consumables(
            self._state.party,
            self._state.pending_loot,
            self._consumable_catalog,
        )
        self._state.pending_loot = remaining

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
            SceneRequest.MODIFIER_SELECT: self._build_modifier_select,
            SceneRequest.DUNGEON_MAP: self._build_dungeon_map,
            SceneRequest.COMBAT: lambda: self._build_combat(data),
            SceneRequest.COMBAT_REWARD: lambda: self._build_combat_reward(data),
            SceneRequest.REST_ROOM: lambda: self._build_rest_room(data),
            SceneRequest.TREASURE_ROOM: lambda: self._build_treasure(data),
            SceneRequest.EVENT_ROOM: lambda: self._build_event(data),
            SceneRequest.CAMPFIRE_ROOM: lambda: self._build_campfire(data),
            SceneRequest.SHOP_ROOM: lambda: self._build_shop(data),
            SceneRequest.EQUIPMENT: self._build_equipment,
            SceneRequest.ITEM_USE: self._build_item_use,
            SceneRequest.LEVEL_UP: lambda: self._build_level_up(data),
            SceneRequest.LOADOUT: self._build_loadout,
            SceneRequest.SUBCLASS_CHOICE: lambda: self._build_subclass_choice(data),
            SceneRequest.TALENT_CHOICE: lambda: self._build_talent_choice(data),
            SceneRequest.GAME_OVER: self._build_game_over,
            SceneRequest.VICTORY: self._build_victory,
        }
        builder = builders.get(target, self._build_main_menu)
        return builder()

    def _build_main_menu(self) -> MainMenuScene:
        set_run_modifier_effect(None)
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
            self._level_system = LevelUpSystem(
                load_xp_table(), load_attribute_points(),
            )
            self._on_scene_complete(
                SceneRequest.PARTY_SELECT, result,
            )

        return PartySelectScene(self._fonts, on_complete=on_done)

    def _build_modifier_select(self) -> ModifierSelectScene:
        all_mods = list(load_modifiers().values())
        rng = Random(self._state.seed)
        offered = rng.sample(all_mods, min(3, len(all_mods)))

        def on_done(result: dict) -> None:
            self._apply_modifiers(result.get("modifiers", []))
            self._on_scene_complete(SceneRequest.MODIFIER_SELECT, result)

        return ModifierSelectScene(self._fonts, offered, on_done)

    def _apply_modifiers(self, modifiers: list) -> None:
        """Armazena modifiers no state e configura efeito global."""
        if self._state is None:
            return
        self._state.active_modifiers = list(modifiers)
        effect = self._state.aggregated_effects
        set_run_modifier_effect(effect)

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
        healing = self._get_healing_mult()
        return RestRoomScene(
            self._fonts,
            self._state.party,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.REST_ROOM, r,
            ),
            healing_mult=healing,
        )

    def _get_healing_mult(self) -> float:
        """Retorna healing_mult do modifier ativo ou 1.0."""
        if self._state is None:
            return 1.0
        return self._state.aggregated_effects.healing_mult

    def _build_combat_reward(self, data: dict) -> CombatRewardScene:
        reward = self._last_reward
        gold_earned = reward.gold_earned if reward else 0
        drops = reward.drops if reward else ()
        total_gold = self._state.gold if self._state else 0
        is_boss = data.get("is_boss", False)
        phys_pts = reward.new_level if reward and reward.leveled_up else 0
        has_pts = self._check_level_points(reward)

        def on_done(result: dict) -> None:
            result["is_boss"] = is_boss
            result["has_points"] = has_pts
            result["new_level"] = new_lvl
            self._on_scene_complete(SceneRequest.COMBAT_REWARD, result)

        xp = reward.xp_earned if reward else 0
        leveled = reward.leveled_up if reward else False
        new_lvl = reward.new_level if reward else 0
        return CombatRewardScene(
            self._fonts, gold_earned, drops,
            total_gold, on_complete=on_done,
            xp_earned=xp, leveled_up=leveled, new_level=new_lvl,
        )

    def _check_level_points(self, reward: CombatRewardResult | None) -> bool:
        """Verifica se o level up deu pontos pra distribuir."""
        if reward is None or not reward.leveled_up:
            return False
        from src.core.progression.attribute_point_config import (
            get_points_for_level,
            load_attribute_points,
        )
        config = load_attribute_points()
        pts = get_points_for_level(reward.new_level, config)
        return pts.total > 0

    def _build_treasure(self, data: dict) -> TreasureScene:
        """Constroi cena de tesouro."""
        node_id = data.get("node_id", "")
        self._combat_node_id = node_id
        rng = Random(self._state.seed + hash(node_id))
        result = resolve_treasure(self._state, rng)
        return TreasureScene(
            self._fonts, result,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.TREASURE_ROOM, r,
            ),
        )

    def _build_event(self, data: dict) -> EventScene:
        """Constroi cena de evento aleatorio."""
        node_id = data.get("node_id", "")
        self._combat_node_id = node_id
        events = load_events()
        rng = Random(self._state.seed + hash(node_id))
        event_id = rng.choice(list(events.keys()))
        event = events[event_id]

        def on_choice(idx: int) -> dict[str, object]:
            choice = event.choices[idx]
            return apply_event_choice(self._state, choice)

        return EventScene(
            self._fonts, event, on_choice,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.EVENT_ROOM, r,
            ),
        )

    def _build_campfire(self, data: dict) -> CampfireScene:
        """Constroi cena de fogueira."""
        node_id = data.get("node_id", "")
        self._combat_node_id = node_id
        buffs = load_campfire_buffs()
        buff_list = list(buffs.values())

        def on_select(idx: int) -> dict[str, object]:
            return apply_campfire_buff(self._state, buff_list[idx])

        return CampfireScene(
            self._fonts, buff_list, on_select,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.CAMPFIRE_ROOM, r,
            ),
        )

    def _build_shop(self, data: dict) -> ShopScene:
        """Constroi cena de loja."""
        node_id = data.get("node_id", "")
        self._combat_node_id = node_id
        shop = load_shop(tier=1)

        def on_buy(idx: int) -> bool:
            return shop.buy(idx, self._state)

        def on_sell(idx: int) -> int:
            return shop.sell(idx, self._state)

        return ShopScene(
            self._fonts, shop, on_buy, on_sell,
            gold_getter=lambda: self._state.gold,
            loot_getter=lambda: self._state.pending_loot,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.SHOP_ROOM, r,
            ),
        )

    def _build_equipment(self) -> EquipmentScene:
        """Constroi cena de equipamento."""
        return EquipmentScene(
            self._fonts,
            self._state.party,
            self._state.equipment_stash,
            self._equipment_catalogs,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.EQUIPMENT, r,
            ),
            gold=self._state.gold,
        )

    def _build_item_use(self) -> ItemUseScene:
        """Constroi cena de uso de itens fora de combate."""
        return ItemUseScene(
            self._fonts,
            self._state.party,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.ITEM_USE, r,
            ),
        )

    def _build_level_up(self, data: dict) -> LevelUpScene:
        """Constroi cena de distribuicao de atributos."""
        from src.core.progression.attribute_point_config import (
            get_points_for_level,
            load_attribute_points,
        )
        config = load_attribute_points()
        new_level = self._last_reward.new_level if self._last_reward else 0
        pts = get_points_for_level(new_level, config)
        is_boss = data.get("is_boss", False)

        def on_done(result: dict) -> None:
            result["is_boss"] = is_boss
            self._on_scene_complete(SceneRequest.LEVEL_UP, result)

        return LevelUpScene(
            self._fonts, self._state.party,
            pts.physical, pts.mental,
            self._level_system, on_complete=on_done,
        )

    def _build_subclass_choice(self, data: dict) -> SubclassChoiceScene:
        """Constroi cena de escolha de subclass pro proximo personagem."""
        registry = load_subclass_registry()
        char_idx = data.get("_subclass_char_idx", 0)
        char = self._state.party[char_idx]
        class_id = type(char).__name__.lower()
        subclasses = registry.get(class_id)
        if subclasses is None:
            self._on_scene_complete(SceneRequest.SUBCLASS_CHOICE, data)
            return SubclassChoiceScene(
                self._fonts, char, registry["fighter"],
                on_complete=lambda r: None,
            )
        is_boss = data.get("is_boss", False)

        def on_done(result: dict) -> None:
            chosen = result.get("subclass")
            if chosen is not None:
                apply_subclass(char, chosen)
            next_idx = char_idx + 1
            if next_idx < len(self._state.party):
                result["_subclass_char_idx"] = next_idx
                result["is_boss"] = is_boss
                result["new_level"] = 3
                self._on_scene_complete(SceneRequest.SUBCLASS_CHOICE, result)
            else:
                result["is_boss"] = is_boss
                self._on_scene_complete(SceneRequest.SUBCLASS_CHOICE, result)

        return SubclassChoiceScene(
            self._fonts, char, subclasses, on_complete=on_done,
        )

    def _build_talent_choice(self, data: dict) -> TalentChoiceScene:
        """Constroi cena de escolha de talento pro proximo personagem."""
        all_talents = load_talents()
        char_idx = data.get("_talent_char_idx", 0)
        char = self._state.party[char_idx]
        class_id = type(char).__name__.lower()
        chosen_ids = data.get("_talent_chosen_ids", set())
        rng = Random(self._state.seed + char_idx + char.level)
        options = generate_talent_offering(
            class_id, all_talents, chosen_ids, rng,
        )
        is_boss = data.get("is_boss", False)
        new_level = data.get("new_level", 0)

        def on_done(result: dict) -> None:
            talent = result.get("talent")
            if talent is not None:
                apply_talent(char, talent)
                chosen_ids.add(talent.talent_id)
            next_idx = char_idx + 1
            if next_idx < len(self._state.party):
                result["_talent_char_idx"] = next_idx
                result["_talent_chosen_ids"] = chosen_ids
                result["is_boss"] = is_boss
                result["new_level"] = new_level
                self._on_scene_complete(SceneRequest.TALENT_CHOICE, result)
            else:
                result["is_boss"] = is_boss
                result["new_level"] = new_level
                self._on_scene_complete(SceneRequest.TALENT_CHOICE, result)

        return TalentChoiceScene(
            self._fonts, char, options, on_complete=on_done,
        )

    def _build_loadout(self) -> LoadoutScene:
        """Constroi cena de customizacao de spell loadout."""
        return LoadoutScene(
            self._fonts, self._state.party,
            on_complete=lambda r: self._on_scene_complete(
                SceneRequest.LOADOUT, r,
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
