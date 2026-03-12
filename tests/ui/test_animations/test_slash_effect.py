"""Testes para SlashEffect animation."""

from src.ui.animations.slash_effect import SlashEffect


class TestSlashEffect:
    def test_starts_not_done(self) -> None:
        s = SlashEffect(x=100, y=50, width=160, height=110)
        assert not s.is_done

    def test_done_after_duration(self) -> None:
        s = SlashEffect(x=100, y=50, width=160, height=110, duration_ms=300)
        s.update(300)
        assert s.is_done

    def test_not_done_before_duration(self) -> None:
        s = SlashEffect(x=100, y=50, width=160, height=110, duration_ms=300)
        s.update(150)
        assert not s.is_done

    def test_is_blocking(self) -> None:
        s = SlashEffect(x=100, y=50, width=160, height=110)
        assert s.blocking

    def test_progress_starts_at_zero(self) -> None:
        s = SlashEffect(x=100, y=50, width=160, height=110)
        assert s.progress == 0.0

    def test_progress_halfway(self) -> None:
        s = SlashEffect(x=100, y=50, width=160, height=110, duration_ms=300)
        s.update(150)
        assert abs(s.progress - 0.5) < 0.01

    def test_progress_clamped_at_one(self) -> None:
        s = SlashEffect(x=100, y=50, width=160, height=110, duration_ms=300)
        s.update(600)
        assert s.progress == 1.0
