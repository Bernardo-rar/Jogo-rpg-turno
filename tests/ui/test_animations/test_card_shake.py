"""Testes para CardShake animation."""

from src.ui.animations.card_shake import CardShake


class TestCardShake:
    def test_starts_not_done(self) -> None:
        cs = CardShake(target_name="Goblin")
        assert not cs.is_done

    def test_done_after_duration(self) -> None:
        cs = CardShake(target_name="Goblin", duration_ms=300)
        cs.update(300)
        assert cs.is_done

    def test_is_blocking(self) -> None:
        cs = CardShake(target_name="Goblin")
        assert cs.blocking

    def test_offset_nonzero_during_animation(self) -> None:
        cs = CardShake(target_name="Goblin", duration_ms=300)
        cs.update(50)
        dx, dy = cs.offset
        assert dx != 0 or dy != 0

    def test_offset_zero_when_done(self) -> None:
        cs = CardShake(target_name="Goblin", duration_ms=300)
        cs.update(300)
        assert cs.offset == (0, 0)

    def test_draw_is_noop(self) -> None:
        cs = CardShake(target_name="Goblin")
        cs.draw(None)  # nao deve crashar

    def test_stores_target_name(self) -> None:
        cs = CardShake(target_name="Goblin")
        assert cs.target_name == "Goblin"
