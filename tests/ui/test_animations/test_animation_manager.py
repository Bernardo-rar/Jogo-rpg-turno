"""Testes para AnimationManager."""

from src.ui.animations.animation_manager import AnimationManager


class FakeAnimation:
    """Animacao fake para testes."""

    def __init__(self, duration_ms: int, *, blocking: bool = True):
        self._duration_ms = duration_ms
        self._elapsed = 0
        self.blocking = blocking
        self.draw_count = 0

    def update(self, dt_ms: int) -> None:
        self._elapsed += dt_ms

    def draw(self, surface: object) -> None:
        self.draw_count += 1

    @property
    def is_done(self) -> bool:
        return self._elapsed >= self._duration_ms


class TestAnimationManager:
    def test_starts_empty(self) -> None:
        mgr = AnimationManager()
        assert not mgr.has_active
        assert not mgr.has_blocking

    def test_spawn_adds_animation(self) -> None:
        mgr = AnimationManager()
        anim = FakeAnimation(100)
        mgr.spawn(anim)
        assert mgr.has_active

    def test_spawn_blocking_sets_has_blocking(self) -> None:
        mgr = AnimationManager()
        mgr.spawn(FakeAnimation(100, blocking=True))
        assert mgr.has_blocking

    def test_spawn_non_blocking_no_has_blocking(self) -> None:
        mgr = AnimationManager()
        mgr.spawn(FakeAnimation(100, blocking=False))
        assert mgr.has_active
        assert not mgr.has_blocking

    def test_update_ticks_all_animations(self) -> None:
        mgr = AnimationManager()
        a1 = FakeAnimation(200)
        a2 = FakeAnimation(300)
        mgr.spawn(a1)
        mgr.spawn(a2)
        mgr.update(200)
        assert a1.is_done
        assert not a2.is_done

    def test_update_removes_finished(self) -> None:
        mgr = AnimationManager()
        mgr.spawn(FakeAnimation(100))
        mgr.update(100)
        assert not mgr.has_active

    def test_draw_calls_all(self) -> None:
        mgr = AnimationManager()
        a1 = FakeAnimation(500)
        a2 = FakeAnimation(500)
        mgr.spawn(a1)
        mgr.spawn(a2)
        mgr.draw(None)
        assert a1.draw_count == 1
        assert a2.draw_count == 1

    def test_blocking_clears_when_done(self) -> None:
        mgr = AnimationManager()
        mgr.spawn(FakeAnimation(100, blocking=True))
        mgr.spawn(FakeAnimation(500, blocking=False))
        mgr.update(100)
        assert mgr.has_active
        assert not mgr.has_blocking

    def test_multiple_blocking(self) -> None:
        mgr = AnimationManager()
        mgr.spawn(FakeAnimation(100, blocking=True))
        mgr.spawn(FakeAnimation(200, blocking=True))
        mgr.update(100)
        assert mgr.has_blocking
        mgr.update(100)
        assert not mgr.has_blocking

    def test_spawn_multiple_then_clear(self) -> None:
        mgr = AnimationManager()
        mgr.spawn(FakeAnimation(100))
        mgr.spawn(FakeAnimation(100))
        mgr.spawn(FakeAnimation(100))
        mgr.update(100)
        assert not mgr.has_active
