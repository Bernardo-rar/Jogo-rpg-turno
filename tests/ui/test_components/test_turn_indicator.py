"""Testes para turn_indicator — logica de pulso e alpha."""

from src.ui.components.turn_indicator import _pulse_alpha, _apply_alpha


class TestPulseAlpha:
    def test_alpha_in_valid_range(self) -> None:
        for ms in range(0, 5000, 100):
            alpha = _pulse_alpha(ms)
            assert 0.3 <= alpha <= 1.1

    def test_varies_over_time(self) -> None:
        values = {_pulse_alpha(ms) for ms in range(0, 2000, 50)}
        assert len(values) > 5


class TestApplyAlpha:
    def test_full_alpha_preserves_color(self) -> None:
        assert _apply_alpha((255, 200, 100), 1.0) == (255, 200, 100)

    def test_half_alpha_halves_color(self) -> None:
        assert _apply_alpha((200, 100, 50), 0.5) == (100, 50, 25)

    def test_zero_alpha_gives_black(self) -> None:
        assert _apply_alpha((255, 255, 255), 0.0) == (0, 0, 0)
