"""Testes para FloatingText animation."""

from src.ui.animations.floating_text import FloatingText


class TestFloatingText:
    def test_starts_not_done(self) -> None:
        ft = FloatingText("-50", x=100, y=200, color=(255, 0, 0))
        assert not ft.is_done

    def test_done_after_duration(self) -> None:
        ft = FloatingText("-50", x=100, y=200, color=(255, 0, 0), duration_ms=800)
        ft.update(800)
        assert ft.is_done

    def test_not_done_before_duration(self) -> None:
        ft = FloatingText("-50", x=100, y=200, color=(255, 0, 0), duration_ms=800)
        ft.update(400)
        assert not ft.is_done

    def test_is_non_blocking(self) -> None:
        ft = FloatingText("-50", x=100, y=200, color=(255, 0, 0))
        assert not ft.blocking

    def test_y_decreases_over_time(self) -> None:
        ft = FloatingText("-50", x=100, y=200, color=(255, 0, 0), duration_ms=800)
        initial_y = ft.current_y
        ft.update(400)
        assert ft.current_y < initial_y

    def test_alpha_decreases_over_time(self) -> None:
        ft = FloatingText("-50", x=100, y=200, color=(255, 0, 0), duration_ms=800)
        initial_alpha = ft.alpha
        ft.update(600)
        assert ft.alpha < initial_alpha

    def test_alpha_starts_at_max(self) -> None:
        ft = FloatingText("-50", x=100, y=200, color=(255, 0, 0))
        assert ft.alpha == 255

    def test_stores_text_and_color(self) -> None:
        ft = FloatingText("+45", x=100, y=200, color=(0, 255, 0))
        assert ft.text == "+45"
        assert ft.color == (0, 255, 0)
