"""Tests for synergy loader."""

from src.core.combat.synergy.synergy_config import SynergyType
from src.core.combat.synergy.synergy_loader import get_synergy, load_synergies


class TestSynergyLoader:

    def test_loads_all_synergies(self) -> None:
        synergies = load_synergies()
        assert len(synergies) >= 5

    def test_healer_dps_pair_exists(self) -> None:
        cfg = get_synergy("healer_dps_pair")
        assert cfg is not None
        assert cfg.synergy_type == SynergyType.PAIR

    def test_pack_tactics_exists(self) -> None:
        cfg = get_synergy("pack_tactics")
        assert cfg is not None
        assert cfg.synergy_type == SynergyType.GROUP
        assert cfg.pack_same_target_bonus_pct == 15.0

    def test_commander_aura_exists(self) -> None:
        cfg = get_synergy("commander_aura")
        assert cfg is not None
        assert cfg.synergy_type == SynergyType.COMMANDER
        assert cfg.commander_aura is not None

    def test_unknown_returns_none(self) -> None:
        assert get_synergy("nonexistent") is None
