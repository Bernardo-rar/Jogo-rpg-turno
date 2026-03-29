"""Tests for QTE evaluator — pure function, no UI."""

from src.core.combat.qte.qte_config import QteOutcome, QteSequence
from src.core.combat.qte.qte_evaluator import evaluate_qte


def _seq(*keys: str) -> QteSequence:
    return QteSequence(keys=tuple(keys))


class TestEvaluateQtePerfect:

    def test_all_correct_is_perfect(self) -> None:
        result = evaluate_qte(
            _seq("LEFT", "UP", "RIGHT"),
            ["LEFT", "UP", "RIGHT"],
        )
        assert result.outcome == QteOutcome.PERFECT
        assert result.correct_count == 3
        assert result.total_count == 3

    def test_perfect_multiplier(self) -> None:
        result = evaluate_qte(
            _seq("LEFT", "UP", "RIGHT"),
            ["LEFT", "UP", "RIGHT"],
        )
        assert result.multiplier == 1.30


class TestEvaluateQtePartial:

    def test_half_correct_is_partial(self) -> None:
        result = evaluate_qte(
            _seq("LEFT", "UP", "RIGHT", "DOWN"),
            ["LEFT", "UP", "DOWN", "LEFT"],
        )
        assert result.outcome == QteOutcome.PARTIAL
        assert result.correct_count == 2

    def test_partial_multiplier(self) -> None:
        result = evaluate_qte(
            _seq("LEFT", "UP", "RIGHT", "DOWN"),
            ["LEFT", "UP", "DOWN", "LEFT"],
        )
        assert result.multiplier == 1.15

    def test_exactly_50_pct_is_partial(self) -> None:
        result = evaluate_qte(
            _seq("L", "U", "R", "D"),
            ["L", "U", "X", "X"],
        )
        assert result.outcome == QteOutcome.PARTIAL


class TestEvaluateQteFailure:

    def test_all_wrong_is_failure(self) -> None:
        result = evaluate_qte(
            _seq("LEFT", "UP", "RIGHT"),
            ["DOWN", "DOWN", "DOWN"],
        )
        assert result.outcome == QteOutcome.FAILURE
        assert result.correct_count == 0

    def test_failure_multiplier(self) -> None:
        result = evaluate_qte(
            _seq("LEFT", "UP", "RIGHT"),
            ["DOWN", "DOWN", "DOWN"],
        )
        assert result.multiplier == 0.90

    def test_below_50_pct_is_failure(self) -> None:
        result = evaluate_qte(
            _seq("L", "U", "R", "D"),
            ["L", "X", "X", "X"],
        )
        assert result.outcome == QteOutcome.FAILURE


class TestEvaluateQteEdgeCases:

    def test_empty_input_is_failure(self) -> None:
        result = evaluate_qte(_seq("L", "U", "R"), [])
        assert result.outcome == QteOutcome.FAILURE
        assert result.correct_count == 0

    def test_partial_input_counts_missing_as_wrong(self) -> None:
        result = evaluate_qte(
            _seq("L", "U", "R", "D"),
            ["L", "U"],
        )
        assert result.total_count == 4
        assert result.correct_count == 2
        assert result.outcome == QteOutcome.PARTIAL

    def test_single_key_correct(self) -> None:
        result = evaluate_qte(_seq("UP"), ["UP"])
        assert result.outcome == QteOutcome.PERFECT

    def test_skipped_returns_neutral(self) -> None:
        result = evaluate_qte(_seq("L", "U"), None)
        assert result.outcome == QteOutcome.SKIPPED
        assert result.multiplier == 1.0


class TestQteSequenceFromDict:

    def test_from_dict(self) -> None:
        data = {
            "keys": ["LEFT", "UP", "RIGHT"],
            "time_window_ms": 2500,
            "difficulty": "HARD",
        }
        seq = QteSequence.from_dict(data)
        assert seq.keys == ("LEFT", "UP", "RIGHT")
        assert seq.time_window_ms == 2500
        assert seq.difficulty == "HARD"

    def test_from_dict_defaults(self) -> None:
        data = {"keys": ["UP"]}
        seq = QteSequence.from_dict(data)
        assert seq.time_window_ms == 2500
        assert seq.difficulty == "MEDIUM"
