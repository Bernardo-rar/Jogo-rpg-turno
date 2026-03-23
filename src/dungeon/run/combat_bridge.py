"""Combat Bridge — prepara e finaliza combates dentro de uma run."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.dungeon.run.run_state import RunState


def prepare_for_combat(party: list[Character]) -> None:
    """Limpa effects residuais antes do combate."""
    for c in party:
        if c.is_alive:
            c.effect_manager.clear_all()


def after_combat(run_state: RunState, node_id: str) -> None:
    """Marca nó visitado e atualiza progresso."""
    node = run_state.floor_map.get_node(node_id)
    if node is not None:
        node.visited = True
    run_state.current_node_id = node_id
    run_state.rooms_cleared += 1
