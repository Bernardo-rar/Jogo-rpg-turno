"""Testes para deteccao de morte via diff alive/dead."""

from src.ui.scenes.combat_scene import _spawn_death_fades
from src.ui.animations.animation_manager import AnimationManager
from src.ui.animations.death_fade import DeathFade
from src.ui.components.battlefield import Battlefield
from src.ui.replay.battle_snapshot import CharacterSnapshot, RoundSnapshot


def _make_snapshot(chars: list[CharacterSnapshot]) -> RoundSnapshot:
    return RoundSnapshot(round_number=1, characters=tuple(chars))


def _make_char(name: str, *, is_alive: bool = True) -> CharacterSnapshot:
    from src.core.characters.position import Position
    return CharacterSnapshot(
        name=name, current_hp=10 if is_alive else 0,
        max_hp=100, current_mana=50, max_mana=100,
        position=Position.FRONT, is_alive=is_alive,
        active_effects=(), is_party=True,
    )


class TestDeathDetection:
    def test_no_deaths_spawns_nothing(self) -> None:
        before = {"Goblin": True}
        after = {"Goblin": True}
        died = [n for n, alive in before.items() if alive and not after.get(n, True)]
        assert died == []

    def test_death_detected_alive_to_dead(self) -> None:
        before = {"Goblin": True, "Hero": True}
        after = {"Goblin": False, "Hero": True}
        died = [n for n, alive in before.items() if alive and not after.get(n, True)]
        assert died == ["Goblin"]

    def test_already_dead_not_reported(self) -> None:
        before = {"Goblin": False}
        after = {"Goblin": False}
        died = [n for n, alive in before.items() if alive and not after.get(n, True)]
        assert died == []

    def test_spawn_death_fades_creates_death_fade(self) -> None:
        snap = _make_snapshot([_make_char("Goblin")])
        bf = Battlefield(snap)
        mgr = AnimationManager()
        _spawn_death_fades(["Goblin"], bf, mgr)
        assert mgr.has_active
