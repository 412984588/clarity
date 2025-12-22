import pytest

from app.models.solve_session import SolveStep
from app.services.state_machine import can_transition, get_next_step, is_final_step


class TestStateMachine:
    def test_valid_transitions(self):
        assert can_transition(SolveStep.RECEIVE, SolveStep.CLARIFY)
        assert can_transition(SolveStep.CLARIFY, SolveStep.REFRAME)
        assert can_transition(SolveStep.REFRAME, SolveStep.OPTIONS)
        assert can_transition(SolveStep.OPTIONS, SolveStep.COMMIT)

    def test_invalid_transitions(self):
        assert not can_transition(SolveStep.RECEIVE, SolveStep.OPTIONS)
        assert not can_transition(SolveStep.CLARIFY, SolveStep.COMMIT)
        assert not can_transition(SolveStep.COMMIT, SolveStep.RECEIVE)
        assert not can_transition(SolveStep.RECEIVE, SolveStep.RECEIVE)

    def test_get_next_step(self):
        assert get_next_step(SolveStep.RECEIVE) == SolveStep.CLARIFY
        assert get_next_step(SolveStep.CLARIFY) == SolveStep.REFRAME
        assert get_next_step(SolveStep.REFRAME) == SolveStep.OPTIONS
        assert get_next_step(SolveStep.OPTIONS) == SolveStep.COMMIT
        assert get_next_step(SolveStep.COMMIT) is None

    def test_is_final_step(self):
        assert is_final_step(SolveStep.COMMIT)
        assert not is_final_step(SolveStep.RECEIVE)
        assert not is_final_step(SolveStep.CLARIFY)
        assert not is_final_step(SolveStep.REFRAME)
        assert not is_final_step(SolveStep.OPTIONS)
