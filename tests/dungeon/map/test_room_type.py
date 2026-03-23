"""Testes para RoomType enum."""

from src.dungeon.map.room_type import RoomType


class TestRoomType:

    def test_has_four_members(self) -> None:
        assert len(RoomType) == 4

    def test_expected_members(self) -> None:
        names = {m.name for m in RoomType}
        assert names == {"COMBAT", "ELITE", "REST", "BOSS"}
