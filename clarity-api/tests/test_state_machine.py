"""State machine transition tests."""

from app.models.solve_session import SolveStep
from app.services.state_machine import get_next_step, validate_transition


def test_valid_transitions():
    assert validate_transition(SolveStep.RECEIVE, SolveStep.CLARIFY)
    assert validate_transition(SolveStep.CLARIFY, SolveStep.REFRAME)
    assert validate_transition(SolveStep.REFRAME, SolveStep.OPTIONS)
    assert validate_transition(SolveStep.OPTIONS, SolveStep.COMMIT)


def test_invalid_transitions():
    assert not validate_transition(SolveStep.RECEIVE, SolveStep.COMMIT)
    assert not validate_transition(SolveStep.CLARIFY, SolveStep.COMMIT)


def test_terminal_state():
    assert get_next_step(SolveStep.COMMIT) is None
    assert not validate_transition(SolveStep.COMMIT, SolveStep.RECEIVE)
