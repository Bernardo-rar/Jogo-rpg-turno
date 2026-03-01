"""Testes para factory functions de buffs e debuffs."""

from src.core.effects.buff_factory import (
    create_combined_buff,
    create_combined_debuff,
    create_flat_buff,
    create_flat_debuff,
    create_percent_buff,
    create_percent_debuff,
)
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_buff import StatBuff
from src.core.effects.stat_debuff import StatDebuff


class TestCreateFlatBuff:

    def test_creates_stat_buff_instance(self) -> None:
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 10, 3)
        assert isinstance(buff, StatBuff)

    def test_flat_value_matches(self) -> None:
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 10, 3)
        assert buff.modifier.flat == 10

    def test_percent_is_zero(self) -> None:
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 10, 3)
        assert buff.modifier.percent == 0.0

    def test_duration_matches(self) -> None:
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 10, 3)
        assert buff.duration == 3


class TestCreatePercentBuff:

    def test_creates_stat_buff_instance(self) -> None:
        buff = create_percent_buff(ModifiableStat.SPEED, 20.0, 5)
        assert isinstance(buff, StatBuff)

    def test_flat_is_zero(self) -> None:
        buff = create_percent_buff(ModifiableStat.SPEED, 20.0, 5)
        assert buff.modifier.flat == 0

    def test_percent_value_matches(self) -> None:
        buff = create_percent_buff(ModifiableStat.SPEED, 20.0, 5)
        assert buff.modifier.percent == 20.0

    def test_duration_matches(self) -> None:
        buff = create_percent_buff(ModifiableStat.SPEED, 20.0, 5)
        assert buff.duration == 5


class TestCreateFlatDebuff:

    def test_creates_stat_debuff_instance(self) -> None:
        debuff = create_flat_debuff(ModifiableStat.PHYSICAL_DEFENSE, 5, 4)
        assert isinstance(debuff, StatDebuff)

    def test_flat_value_is_negated(self) -> None:
        debuff = create_flat_debuff(ModifiableStat.PHYSICAL_DEFENSE, 5, 4)
        assert debuff.modifier.flat == -5

    def test_percent_is_zero(self) -> None:
        debuff = create_flat_debuff(ModifiableStat.PHYSICAL_DEFENSE, 5, 4)
        assert debuff.modifier.percent == 0.0

    def test_duration_matches(self) -> None:
        debuff = create_flat_debuff(ModifiableStat.PHYSICAL_DEFENSE, 5, 4)
        assert debuff.duration == 4


class TestCreatePercentDebuff:

    def test_creates_stat_debuff_instance(self) -> None:
        debuff = create_percent_debuff(ModifiableStat.SPEED, 15.0, 3)
        assert isinstance(debuff, StatDebuff)

    def test_flat_is_zero(self) -> None:
        debuff = create_percent_debuff(ModifiableStat.SPEED, 15.0, 3)
        assert debuff.modifier.flat == 0

    def test_percent_value_is_negated(self) -> None:
        debuff = create_percent_debuff(ModifiableStat.SPEED, 15.0, 3)
        assert debuff.modifier.percent == -15.0

    def test_duration_matches(self) -> None:
        debuff = create_percent_debuff(ModifiableStat.SPEED, 15.0, 3)
        assert debuff.duration == 3


class TestCreateCombinedBuff:

    def test_create_combined_buff(self) -> None:
        buff = create_combined_buff(
            ModifiableStat.PHYSICAL_ATTACK, flat=10, percent=20.0, duration=3,
        )
        assert isinstance(buff, StatBuff)
        assert buff.modifier.flat == 10
        assert buff.modifier.percent == 20.0
        assert buff.duration == 3


class TestCreateCombinedDebuff:

    def test_create_combined_debuff(self) -> None:
        debuff = create_combined_debuff(
            ModifiableStat.PHYSICAL_DEFENSE, flat=5, percent=15.0, duration=4,
        )
        assert isinstance(debuff, StatDebuff)
        assert debuff.modifier.flat == -5
        assert debuff.modifier.percent == -15.0
        assert debuff.duration == 4
