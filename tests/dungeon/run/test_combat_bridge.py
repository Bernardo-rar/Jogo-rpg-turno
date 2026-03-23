"""Testes para combat_bridge."""

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_buff import StatBuff
from src.core.effects.stat_modifier import StatModifier
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.run.combat_bridge import after_combat, prepare_for_combat
from src.dungeon.run.run_state import RunState
from tests.core.test_combat.conftest import _build_char


class TestPrepareForCombat:

    def test_clears_effects_on_alive(self) -> None:
        char = _build_char("A")
        mod = StatModifier(stat=ModifiableStat.PHYSICAL_ATTACK, flat=5)
        buff = StatBuff(modifier=mod, duration=3)
        char.effect_manager.add_effect(buff)
        assert len(char.effect_manager.active_effects) > 0
        prepare_for_combat([char])
        assert len(char.effect_manager.active_effects) == 0

    def test_skips_dead_characters(self) -> None:
        char = _build_char("A")
        char.take_damage(char.max_hp)
        assert not char.is_alive
        # Nao deve dar erro em mortos
        prepare_for_combat([char])


class TestAfterCombat:

    def test_marks_node_visited(self) -> None:
        fm = MapGenerator().generate(seed=1)
        state = RunState(seed=1, party=[], floor_map=fm)
        node_id = fm.layers[0][0].node_id
        after_combat(state, node_id)
        assert fm.get_node(node_id).visited is True

    def test_updates_current_node(self) -> None:
        fm = MapGenerator().generate(seed=1)
        state = RunState(seed=1, party=[], floor_map=fm)
        node_id = fm.layers[0][0].node_id
        after_combat(state, node_id)
        assert state.current_node_id == node_id

    def test_increments_rooms_cleared(self) -> None:
        fm = MapGenerator().generate(seed=1)
        state = RunState(seed=1, party=[], floor_map=fm)
        node_id = fm.layers[0][0].node_id
        after_combat(state, node_id)
        assert state.rooms_cleared == 1
