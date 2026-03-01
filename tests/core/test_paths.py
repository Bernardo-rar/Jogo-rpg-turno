"""Testes para utilitario de resolucao de caminhos."""

from pathlib import Path

from src.core._paths import get_project_root, resolve_data_path


class TestGetProjectRoot:

    def test_returns_directory_with_pyproject(self) -> None:
        root = get_project_root()
        assert (root / "pyproject.toml").is_file()

    def test_returns_path_type(self) -> None:
        root = get_project_root()
        assert isinstance(root, Path)

    def test_data_directory_exists(self) -> None:
        root = get_project_root()
        assert (root / "data").is_dir()


class TestResolveDataPath:

    def test_relative_path_resolved_from_root(self) -> None:
        path = resolve_data_path("data/elements/elemental_profiles.json")
        assert path.is_file()

    def test_absolute_path_returned_unchanged(self) -> None:
        root = get_project_root()
        absolute = root / "some" / "absolute" / "path.json"
        assert resolve_data_path(str(absolute)) == absolute


class TestGetProjectRootNotFound:

    def test_raises_when_marker_not_found(self, tmp_path, monkeypatch) -> None:
        """Se nenhum parent contiver pyproject.toml, deve levantar FileNotFoundError."""
        import src.core._paths as paths_mod

        monkeypatch.setattr(
            paths_mod, "_MARKER", "NONEXISTENT_MARKER_FILE_12345.toml",
        )
        import pytest
        with pytest.raises(FileNotFoundError, match="NONEXISTENT_MARKER"):
            get_project_root()
