"""Testes para ComboConfig e loader de combos elementais."""

from __future__ import annotations

from src.core.elements.combo.combo_config import (
    ComboConfig,
    ComboEffect,
    load_combo_configs,
)
from src.core.elements.element_type import ElementType

EXPECTED_COMBO_COUNT = 6


def test_load_combo_configs_returns_six() -> None:
    """JSON deve carregar exatamente 6 combos."""
    combos = load_combo_configs()

    assert len(combos) == EXPECTED_COMBO_COUNT


def test_combo_key_is_frozenset() -> None:
    """Chave do dict deve ser frozenset de 2 ElementTypes."""
    combos = load_combo_configs()

    for key in combos:
        assert isinstance(key, frozenset)
        assert len(key) == 2
        for elem in key:
            assert isinstance(elem, ElementType)


def test_combo_from_dict() -> None:
    """from_dict deve parsear corretamente os campos do JSON."""
    raw = {
        "combo_name": "Test Combo",
        "element_a": "FIRE",
        "element_b": "ICE",
        "effect": {
            "ailment_id": "freeze",
            "ailment_duration": 3,
            "bonus_damage": 15,
        },
    }

    config = ComboConfig.from_dict(raw)

    assert config.combo_name == "Test Combo"
    assert config.element_a == ElementType.FIRE
    assert config.element_b == ElementType.ICE
    assert config.effect.ailment_id == "freeze"
    assert config.effect.ailment_duration == 3
    assert config.effect.bonus_damage == 15


def test_combo_effect_defaults() -> None:
    """ComboEffect deve ter defaults zero para campos omitidos."""
    effect = ComboEffect()

    assert effect.ailment_id == ""
    assert effect.ailment_power == 0
    assert effect.ailment_duration == 0
    assert effect.bonus_damage == 0


def test_combo_consumes_markers_default_true() -> None:
    """consumes_markers deve defaultar para True."""
    raw = {
        "combo_name": "Test",
        "element_a": "FIRE",
        "element_b": "ICE",
        "effect": {},
    }

    config = ComboConfig.from_dict(raw)

    assert config.consumes_markers is True


def test_combo_lookup_order_independent() -> None:
    """Frozenset{FIRE, ICE} == frozenset{ICE, FIRE}."""
    combos = load_combo_configs()

    key_a = frozenset({ElementType.FIRE, ElementType.ICE})
    key_b = frozenset({ElementType.ICE, ElementType.FIRE})

    assert key_a in combos
    assert key_b in combos
    assert combos[key_a] is combos[key_b]
