"""QTE evaluator — pure function, no UI dependency."""

from __future__ import annotations

from src.core.combat.qte.qte_config import (
    FAILURE_MULT,
    PARTIAL_MULT,
    PARTIAL_THRESHOLD,
    PERFECT_MULT,
    SKIPPED_MULT,
    QteOutcome,
    QteResult,
    QteSequence,
)


def evaluate_qte(
    sequence: QteSequence,
    inputs: list[str] | None,
) -> QteResult:
    """Evaluates player inputs against the QTE sequence.

    Args:
        sequence: The expected key sequence.
        inputs: Player's key presses, or None if skipped/disabled.

    Returns:
        QteResult with outcome and multiplier.
    """
    if inputs is None:
        return QteResult(
            outcome=QteOutcome.SKIPPED,
            correct_count=0,
            total_count=len(sequence.keys),
            multiplier=SKIPPED_MULT,
        )
    total = len(sequence.keys)
    correct = _count_correct(sequence.keys, inputs)
    outcome = _determine_outcome(correct, total)
    multiplier = _OUTCOME_MULT[outcome]
    return QteResult(
        outcome=outcome,
        correct_count=correct,
        total_count=total,
        multiplier=multiplier,
    )


def _count_correct(
    expected: tuple[str, ...], actual: list[str],
) -> int:
    correct = 0
    for i, key in enumerate(expected):
        if i < len(actual) and actual[i] == key:
            correct += 1
    return correct


def _determine_outcome(correct: int, total: int) -> QteOutcome:
    if total == 0:
        return QteOutcome.SKIPPED
    ratio = correct / total
    if ratio >= 1.0:
        return QteOutcome.PERFECT
    if ratio >= PARTIAL_THRESHOLD:
        return QteOutcome.PARTIAL
    return QteOutcome.FAILURE


_OUTCOME_MULT: dict[QteOutcome, float] = {
    QteOutcome.PERFECT: PERFECT_MULT,
    QteOutcome.PARTIAL: PARTIAL_MULT,
    QteOutcome.FAILURE: FAILURE_MULT,
    QteOutcome.SKIPPED: SKIPPED_MULT,
}
