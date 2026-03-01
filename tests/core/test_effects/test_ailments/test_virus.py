"""Testes para Virus - DoT potencializado."""

from src.core.effects.ailments.virus import Virus
from src.core.effects.effect_category import EffectCategory


class TestVirusCreation:

    def test_create_with_damage_and_duration(self) -> None:
        virus = Virus(damage_per_tick=12, duration=4)
        assert virus.damage_per_tick == 12
        assert virus.duration == 4

    def test_name_is_virus(self) -> None:
        virus = Virus(damage_per_tick=12, duration=4)
        assert virus.name == "Virus"

    def test_ailment_id_is_virus(self) -> None:
        virus = Virus(damage_per_tick=12, duration=4)
        assert virus.ailment_id == "virus"

    def test_stacking_key(self) -> None:
        virus = Virus(damage_per_tick=12, duration=4)
        assert virus.stacking_key == "ailment_virus"


class TestVirusBehavior:

    def test_tick_deals_damage(self) -> None:
        virus = Virus(damage_per_tick=15, duration=3)
        result = virus.tick()
        assert result.damage == 15

    def test_tick_message_includes_virus(self) -> None:
        virus = Virus(damage_per_tick=15, duration=3)
        result = virus.tick()
        assert "Virus" in result.message
