"""Testes para BuffAura animation."""

from src.ui.animations.buff_aura import BuffAura


class TestBuffAura:
    def test_starts_not_done(self) -> None:
        ba = BuffAura(x=100, y=50, width=160, height=110, color=(80, 200, 80))
        assert not ba.is_done

    def test_done_after_duration(self) -> None:
        ba = BuffAura(x=100, y=50, width=160, height=110, color=(80, 200, 80), duration_ms=600)
        ba.update(600)
        assert ba.is_done

    def test_is_non_blocking(self) -> None:
        ba = BuffAura(x=100, y=50, width=160, height=110, color=(80, 200, 80))
        assert not ba.blocking

    def test_stores_color(self) -> None:
        color = (200, 80, 80)
        ba = BuffAura(x=100, y=50, width=160, height=110, color=color)
        assert ba.color == color
