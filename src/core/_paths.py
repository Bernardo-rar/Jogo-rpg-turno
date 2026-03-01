"""Utilitario para resolver caminhos relativos ao root do projeto."""

from __future__ import annotations

from pathlib import Path

_MARKER = "pyproject.toml"


def get_project_root() -> Path:
    """Sobe a arvore de diretorios ate encontrar pyproject.toml."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / _MARKER).is_file():
            return current
        current = current.parent
    msg = f"Could not find {_MARKER} in any parent directory"
    raise FileNotFoundError(msg)


def resolve_data_path(relative: str) -> Path:
    """Resolve caminho relativo ao root do projeto.

    Se o path ja for absoluto, retorna sem alteracao.
    """
    path = Path(relative)
    if path.is_absolute():
        return path
    return get_project_root() / path
