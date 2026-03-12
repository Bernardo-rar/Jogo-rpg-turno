"""Testes para PoisonBubbles animation."""

from src.ui.animations.poison_bubbles import PoisonBubbles


class TestPoisonBubbles:
    def test_starts_not_done(self) -> None:
        pb = PoisonBubbles(x=100, y=50, width=160, height=110)
        assert not pb.is_done

    def test_done_after_duration(self) -> None:
        pb = PoisonBubbles(x=100, y=50, width=160, height=110, duration_ms=500)
        pb.update(500)
        assert pb.is_done

    def test_is_non_blocking(self) -> None:
        pb = PoisonBubbles(x=100, y=50, width=160, height=110)
        assert not pb.blocking

    def test_creates_bubbles(self) -> None:
        pb = PoisonBubbles(x=100, y=50, width=160, height=110)
        assert pb.bubble_count > 0
