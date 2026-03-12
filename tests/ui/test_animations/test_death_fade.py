"""Testes para DeathFade animation."""

from src.ui.animations.death_fade import DeathFade


class TestDeathFade:
    def test_starts_not_done(self) -> None:
        df = DeathFade(x=100, y=50, width=160, height=110)
        assert not df.is_done

    def test_done_after_duration(self) -> None:
        df = DeathFade(x=100, y=50, width=160, height=110, duration_ms=800)
        df.update(800)
        assert df.is_done

    def test_is_non_blocking(self) -> None:
        df = DeathFade(x=100, y=50, width=160, height=110)
        assert not df.blocking

    def test_alpha_starts_at_zero(self) -> None:
        df = DeathFade(x=100, y=50, width=160, height=110)
        assert df.alpha == 0

    def test_alpha_increases_over_time(self) -> None:
        df = DeathFade(x=100, y=50, width=160, height=110, duration_ms=800)
        df.update(400)
        assert df.alpha > 0

    def test_alpha_capped(self) -> None:
        df = DeathFade(x=100, y=50, width=160, height=110, duration_ms=800)
        df.update(800)
        assert df.alpha <= 180
