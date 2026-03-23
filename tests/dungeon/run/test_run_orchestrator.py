"""Testes para RunOrchestrator."""

from src.dungeon.map.room_type import RoomType
from src.dungeon.run.run_orchestrator import RunOrchestrator, SceneRequest


class TestRunOrchestrator:

    def test_main_menu_leads_to_party_select(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(SceneRequest.MAIN_MENU, {"action": "play"})
        assert t.target == SceneRequest.PARTY_SELECT

    def test_party_select_leads_to_dungeon_map(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(SceneRequest.PARTY_SELECT, {"class_ids": []})
        assert t.target == SceneRequest.DUNGEON_MAP

    def test_dungeon_map_combat_leads_to_combat(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(
            SceneRequest.DUNGEON_MAP,
            {"room_type": RoomType.COMBAT, "node_id": "L0_N0"},
        )
        assert t.target == SceneRequest.COMBAT

    def test_dungeon_map_elite_leads_to_combat(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(
            SceneRequest.DUNGEON_MAP,
            {"room_type": RoomType.ELITE, "node_id": "L1_N0"},
        )
        assert t.target == SceneRequest.COMBAT

    def test_dungeon_map_rest_leads_to_rest_room(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(
            SceneRequest.DUNGEON_MAP,
            {"room_type": RoomType.REST, "node_id": "L2_N0"},
        )
        assert t.target == SceneRequest.REST_ROOM

    def test_dungeon_map_boss_leads_to_combat(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(
            SceneRequest.DUNGEON_MAP,
            {"room_type": RoomType.BOSS, "node_id": "BOSS"},
        )
        assert t.target == SceneRequest.COMBAT

    def test_combat_victory_non_boss_returns_to_map(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(
            SceneRequest.COMBAT,
            {"victory": True, "is_boss": False, "party_alive": True},
        )
        assert t.target == SceneRequest.DUNGEON_MAP

    def test_combat_victory_boss_leads_to_victory(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(
            SceneRequest.COMBAT,
            {"victory": True, "is_boss": True, "party_alive": True},
        )
        assert t.target == SceneRequest.VICTORY

    def test_combat_defeat_party_dead_leads_to_game_over(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(
            SceneRequest.COMBAT,
            {"victory": False, "is_boss": False, "party_alive": False},
        )
        assert t.target == SceneRequest.GAME_OVER

    def test_combat_defeat_party_alive_returns_to_map(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(
            SceneRequest.COMBAT,
            {"victory": False, "is_boss": False, "party_alive": True},
        )
        assert t.target == SceneRequest.DUNGEON_MAP

    def test_rest_room_returns_to_map(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(SceneRequest.REST_ROOM, {})
        assert t.target == SceneRequest.DUNGEON_MAP

    def test_game_over_returns_to_menu(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(SceneRequest.GAME_OVER, {})
        assert t.target == SceneRequest.MAIN_MENU

    def test_victory_returns_to_menu(self) -> None:
        orch = RunOrchestrator()
        t = orch.on_scene_complete(SceneRequest.VICTORY, {})
        assert t.target == SceneRequest.MAIN_MENU
