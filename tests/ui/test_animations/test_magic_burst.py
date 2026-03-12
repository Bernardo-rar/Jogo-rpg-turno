"""Testes para MagicBurst animation."""

from src.ui.animations.magic_burst import MagicBurst


class TestMagicBurst:
    def test_starts_not_done(self) -> None:
        mb = MagicBurst(cx=200, cy=100, color=(255, 120, 30))
        assert not mb.is_done

    def test_done_after_duration(self) -> None:
        mb = MagicBurst(cx=200, cy=100, color=(255, 120, 30), duration_ms=500)
        mb.update(500)
        assert mb.is_done

    def test_is_blocking(self) -> None:
        mb = MagicBurst(cx=200, cy=100, color=(255, 120, 30))
        assert mb.blocking

    def test_radius_increases_over_time(self) -> None:
        mb = MagicBurst(cx=200, cy=100, color=(255, 120, 30), duration_ms=500)
        r1 = mb.current_radius
        mb.update(250)
        assert mb.current_radius > r1

    def test_stores_color(self) -> None:
        color = (130, 200, 255)
        mb = MagicBurst(cx=200, cy=100, color=color)
        assert mb.color == color

    def test_alpha_decreases_over_time(self) -> None:
        mb = MagicBurst(cx=200, cy=100, color=(255, 120, 30), duration_ms=500)
        a1 = mb.alpha
        mb.update(400)
        assert mb.alpha < a1
