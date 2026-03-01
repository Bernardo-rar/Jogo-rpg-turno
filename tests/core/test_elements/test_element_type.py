"""Testes para ElementType enum - 10 elementos do sistema elemental."""

from src.core.elements.element_type import ElementType


class TestElementTypeMembers:

    def test_has_fire(self) -> None:
        assert isinstance(ElementType.FIRE, ElementType)

    def test_has_water(self) -> None:
        assert isinstance(ElementType.WATER, ElementType)

    def test_has_ice(self) -> None:
        assert isinstance(ElementType.ICE, ElementType)

    def test_has_lightning(self) -> None:
        assert isinstance(ElementType.LIGHTNING, ElementType)

    def test_has_earth(self) -> None:
        assert isinstance(ElementType.EARTH, ElementType)

    def test_has_holy(self) -> None:
        assert isinstance(ElementType.HOLY, ElementType)

    def test_has_darkness(self) -> None:
        assert isinstance(ElementType.DARKNESS, ElementType)

    def test_has_celestial(self) -> None:
        assert isinstance(ElementType.CELESTIAL, ElementType)

    def test_has_psychic(self) -> None:
        assert isinstance(ElementType.PSYCHIC, ElementType)

    def test_has_force(self) -> None:
        assert isinstance(ElementType.FORCE, ElementType)


class TestElementTypeProperties:

    def test_has_exactly_ten_elements(self) -> None:
        assert len(list(ElementType)) == 10

    def test_all_values_are_unique(self) -> None:
        values = [e.value for e in ElementType]
        assert len(values) == len(set(values))
