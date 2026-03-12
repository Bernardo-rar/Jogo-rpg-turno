"""Testes para HealParticles animation."""

from src.ui.animations.heal_particles import HealParticles


class TestHealParticles:
    def test_starts_not_done(self) -> None:
        hp = HealParticles(x=100, y=50, width=160, height=110)
        assert not hp.is_done

    def test_done_after_duration(self) -> None:
        hp = HealParticles(x=100, y=50, width=160, height=110, duration_ms=400)
        hp.update(400)
        assert hp.is_done

    def test_not_done_before_duration(self) -> None:
        hp = HealParticles(x=100, y=50, width=160, height=110, duration_ms=400)
        hp.update(200)
        assert not hp.is_done

    def test_is_blocking(self) -> None:
        hp = HealParticles(x=100, y=50, width=160, height=110)
        assert hp.blocking

    def test_creates_particles(self) -> None:
        hp = HealParticles(x=100, y=50, width=160, height=110)
        assert hp.particle_count > 0
