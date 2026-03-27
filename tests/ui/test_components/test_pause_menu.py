"""Testes para pause_menu — handle_pause_input retorna resultado correto."""

import pygame

from src.ui.components.pause_menu import PauseMenuResult, handle_pause_input


def test_handle_pause_resume() -> None:
    result = handle_pause_input(pygame.K_1)
    assert result == PauseMenuResult.RESUME


def test_handle_pause_help() -> None:
    result = handle_pause_input(pygame.K_2)
    assert result == PauseMenuResult.HELP


def test_handle_pause_forfeit() -> None:
    result = handle_pause_input(pygame.K_3)
    assert result == PauseMenuResult.FORFEIT


def test_handle_pause_escape_resumes() -> None:
    result = handle_pause_input(pygame.K_ESCAPE)
    assert result == PauseMenuResult.RESUME


def test_handle_pause_unknown_returns_none() -> None:
    result = handle_pause_input(pygame.K_a)
    assert result is None
