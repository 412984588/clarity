from datetime import datetime
from uuid import uuid4

import pytest
from app.models.learn_session import LearnSession
from app.routers.learn.utils import (
    _build_context_prompt,
    _generate_review_schedule,
    _validate_session,
)
from fastapi import HTTPException


def test_validate_session_returns_active_session():
    # Arrange
    session = LearnSession(id=uuid4(), user_id=uuid4(), status="active")

    # Act
    result = _validate_session(session)

    # Assert
    assert result is session


def test_validate_session_raises_when_missing():
    # Arrange
    session = None

    # Act
    with pytest.raises(HTTPException) as excinfo:
        learn_router._validate_session(session)

    # Assert
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == {"error": "SESSION_NOT_FOUND"}


def test_validate_session_raises_when_inactive():
    # Arrange
    session = LearnSession(id=uuid4(), user_id=uuid4(), status="completed")

    # Act
    with pytest.raises(HTTPException) as excinfo:
        learn_router._validate_session(session)

    # Assert
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == {"error": "SESSION_NOT_ACTIVE"}


def test_build_context_prompt_returns_current_message_without_history():
    # Arrange
    history = []
    message = "current"

    # Act
    result = _build_context_prompt(history, message)

    # Assert
    assert result == "current"


def test_build_context_prompt_includes_recent_history_only():
    # Arrange
    history = [
        {"role": "user", "content": f"u-{index}"}
        if index % 2 == 0
        else {"role": "assistant", "content": f"a-{index}"}
        for index in range(7)
    ]
    message = "current"

    # Act
    result = _build_context_prompt(history, message)

    # Assert
    assert "u-0" not in result
    assert "a-1" in result
    assert "Assistant: a-1" in result
    assert "User: u-2" in result
    assert "Current message: current" in result


def test_generate_review_schedule_uses_expected_offsets(monkeypatch):
    # Arrange
    fixed_now = datetime(2024, 1, 1, 12, 0, 0)
    monkeypatch.setattr("app.routers.learn.utils.utc_now", lambda: fixed_now)

    # Act
    result = _generate_review_schedule()

    # Assert
    assert result["day_1"] == datetime(2024, 1, 2, 12, 0, 0).isoformat()
    assert result["day_3"] == datetime(2024, 1, 4, 12, 0, 0).isoformat()
    assert result["day_7"] == datetime(2024, 1, 8, 12, 0, 0).isoformat()
    assert result["day_15"] == datetime(2024, 1, 16, 12, 0, 0).isoformat()
    assert result["day_30"] == datetime(2024, 1, 31, 12, 0, 0).isoformat()
