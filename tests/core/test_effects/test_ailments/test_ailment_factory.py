"""Testes para ailment_factory - factory functions de ailments."""

from src.core.effects.ailments.ailment_factory import (
    create_amnesia,
    create_bleed,
    create_burn,
    create_cold,
    create_confusion,
    create_curse,
    create_freeze,
    create_injury,
    create_paralysis,
    create_poison,
    create_scorch,
    create_sickness,
    create_virus,
    create_weakness,
)
from src.core.effects.ailments.amnesia import Amnesia
from src.core.effects.ailments.confusion import Confusion
from src.core.effects.ailments.bleed import Bleed
from src.core.effects.ailments.burn import Burn
from src.core.effects.ailments.cold import Cold
from src.core.effects.ailments.curse import Curse
from src.core.effects.ailments.freeze import Freeze
from src.core.effects.ailments.injury import Injury
from src.core.effects.ailments.paralysis import Paralysis
from src.core.effects.ailments.poison import Poison
from src.core.effects.ailments.scorch import Scorch
from src.core.effects.ailments.sickness import Sickness
from src.core.effects.ailments.virus import Virus
from src.core.effects.ailments.weakness import Weakness


class TestCreatePoison:

    def test_returns_poison_instance(self) -> None:
        result = create_poison(damage_per_tick=5, duration=3)
        assert isinstance(result, Poison)

    def test_damage_matches(self) -> None:
        result = create_poison(damage_per_tick=8, duration=4)
        assert result.damage_per_tick == 8
        assert result.duration == 4


class TestCreateVirus:

    def test_returns_virus_instance(self) -> None:
        result = create_virus(damage_per_tick=12, duration=3)
        assert isinstance(result, Virus)

    def test_damage_matches(self) -> None:
        result = create_virus(damage_per_tick=15, duration=5)
        assert result.damage_per_tick == 15


class TestCreateBleed:

    def test_returns_bleed_instance(self) -> None:
        result = create_bleed(damage_per_tick=6, duration=4)
        assert isinstance(result, Bleed)

    def test_damage_matches(self) -> None:
        result = create_bleed(damage_per_tick=10, duration=3)
        assert result.damage_per_tick == 10


class TestCreateBurn:

    def test_returns_burn_instance(self) -> None:
        result = create_burn(damage_per_tick=10, duration=3)
        assert isinstance(result, Burn)

    def test_damage_matches(self) -> None:
        result = create_burn(damage_per_tick=12, duration=4)
        assert result.damage_per_tick == 12


class TestCreateScorch:

    def test_returns_scorch_instance(self) -> None:
        result = create_scorch(damage_per_tick=20, duration=3)
        assert isinstance(result, Scorch)

    def test_damage_matches(self) -> None:
        result = create_scorch(damage_per_tick=25, duration=2)
        assert result.damage_per_tick == 25


class TestCreateFreeze:

    def test_returns_freeze_instance(self) -> None:
        result = create_freeze(duration=2)
        assert isinstance(result, Freeze)

    def test_duration_matches(self) -> None:
        result = create_freeze(duration=3)
        assert result.duration == 3


class TestCreateParalysis:

    def test_returns_paralysis_instance(self) -> None:
        result = create_paralysis(duration=4)
        assert isinstance(result, Paralysis)

    def test_duration_matches(self) -> None:
        result = create_paralysis(duration=5)
        assert result.duration == 5


class TestCreateCold:

    def test_returns_cold_instance(self) -> None:
        result = create_cold(duration=3, reduction_percent=20.0)
        assert isinstance(result, Cold)

    def test_modifier_matches(self) -> None:
        result = create_cold(duration=3, reduction_percent=25.0)
        assert result.get_modifiers()[0].percent == -25.0


class TestCreateWeakness:

    def test_returns_weakness_instance(self) -> None:
        result = create_weakness(duration=3, reduction_percent=20.0)
        assert isinstance(result, Weakness)

    def test_returns_two_modifiers(self) -> None:
        result = create_weakness(duration=3, reduction_percent=15.0)
        assert len(result.get_modifiers()) == 2


class TestCreateInjury:

    def test_returns_injury_instance(self) -> None:
        result = create_injury(duration=3, reduction_percent=20.0)
        assert isinstance(result, Injury)

    def test_returns_two_modifiers(self) -> None:
        result = create_injury(duration=3, reduction_percent=15.0)
        assert len(result.get_modifiers()) == 2


class TestCreateSickness:

    def test_returns_sickness_instance(self) -> None:
        result = create_sickness(duration=3, reduction_percent=30.0)
        assert isinstance(result, Sickness)

    def test_modifier_matches(self) -> None:
        result = create_sickness(duration=3, reduction_percent=40.0)
        assert result.get_modifiers()[0].percent == -40.0


class TestCreateAmnesia:

    def test_returns_amnesia_instance(self) -> None:
        result = create_amnesia(duration=3)
        assert isinstance(result, Amnesia)

    def test_duration_matches(self) -> None:
        result = create_amnesia(duration=4)
        assert result.duration == 4


class TestCreateConfusion:

    def test_returns_confusion_instance(self) -> None:
        result = create_confusion(duration=3)
        assert isinstance(result, Confusion)

    def test_duration_matches(self) -> None:
        result = create_confusion(duration=4)
        assert result.duration == 4


class TestCreateCurse:

    def test_returns_curse_instance(self) -> None:
        result = create_curse(duration=3)
        assert isinstance(result, Curse)

    def test_duration_matches(self) -> None:
        result = create_curse(duration=5)
        assert result.duration == 5
