from src.core.characters.position import Position


class TestPosition:
    def test_has_front_position(self):
        assert Position.FRONT is not None

    def test_has_back_position(self):
        assert Position.BACK is not None

    def test_only_two_positions(self):
        assert len(list(Position)) == 2
