# tests/test_scheduler_facade.py
"""
Tests for SchedulerFacade (Facade design pattern).

Run with:  pytest tests/test_scheduler_facade.py -v

These tests mock SchedulerModel and ConfigModel so they run without
a real config file or scheduler installation.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from scheduler_facade import SchedulerFacade


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_model(schedules: list[list] | None = None) -> MagicMock:
    """
    Build a mock SchedulerModel that yields the given schedules.

    Parameters:
        schedules (list[list] | None): Schedules to return from
            generate_schedules(). Defaults to [[mock_course]].
    Returns:
        MagicMock: Configured mock SchedulerModel.
    """
    if schedules is None:
        schedules = [[MagicMock(course_str="CMSC 101.01")]]

    model = MagicMock()
    model.config_model = MagicMock()
    model.config_model.config = MagicMock()
    model.config_model.config.limit = 100
    model.generate_schedules.return_value = iter(schedules)
    return model


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

class TestSchedulerFacadeInit:
    def test_stores_model_reference(self) -> None:
        model = _make_model()
        facade = SchedulerFacade(model)
        assert facade._model is model


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestSchedulerFacadeValidation:
    def test_raises_when_model_is_none(self) -> None:
        facade = SchedulerFacade(None)
        with pytest.raises(RuntimeError, match="No scheduler model"):
            facade.generate(limit=1)

    def test_raises_when_config_model_is_none(self) -> None:
        model = MagicMock()
        model.config_model = None
        facade = SchedulerFacade(model)
        with pytest.raises(RuntimeError, match="No configuration loaded"):
            facade.generate(limit=1)


# ---------------------------------------------------------------------------
# Progress callback
# ---------------------------------------------------------------------------

class TestSchedulerFacadeProgress:
    def test_callback_called_on_each_milestone(self) -> None:
        model = _make_model()
        events: list[tuple[int, str]] = []
        facade = SchedulerFacade(model)
        facade.generate(limit=1, progress_callback=lambda p, m: events.append((p, m)))

        percents = [p for p, _ in events]
        assert percents[0] == 0, "Must start at 0 %"
        assert percents[-1] == 100, "Must end at 100 %"

    def test_progress_is_non_decreasing(self) -> None:
        schedules = [[MagicMock()] for _ in range(5)]
        model = _make_model(schedules=schedules)
        percents: list[int] = []
        SchedulerFacade(model).generate(
            limit=5,
            progress_callback=lambda p, _: percents.append(p),
        )
        assert percents == sorted(percents), "Progress must never go backwards"

    def test_callback_receives_string_messages(self) -> None:
        model = _make_model()
        messages: list[str] = []
        SchedulerFacade(model).generate(
            limit=1,
            progress_callback=lambda _, m: messages.append(m),
        )
        assert all(isinstance(m, str) for m in messages)
        assert len(messages) > 0

    def test_no_callback_runs_silently(self) -> None:
        """Passing no callback must not raise."""
        model = _make_model()
        result = SchedulerFacade(model).generate(limit=1)
        assert isinstance(result, list)

    def test_incremental_progress_per_schedule(self) -> None:
        """Each collected schedule should trigger a distinct callback call."""
        n = 4
        schedules = [[MagicMock()] for _ in range(n)]
        model = _make_model(schedules=schedules)
        percents: list[int] = []
        SchedulerFacade(model).generate(
            limit=n,
            progress_callback=lambda p, _: percents.append(p),
        )
        # There should be at least n distinct percent values between 40 and 95
        mid = [p for p in percents if 40 <= p <= 95]
        assert len(mid) >= n


# ---------------------------------------------------------------------------
# Return value
# ---------------------------------------------------------------------------

class TestSchedulerFacadeResult:
    def test_returns_all_schedules(self) -> None:
        schedules = [[MagicMock()] for _ in range(3)]
        model = _make_model(schedules=schedules)
        result = SchedulerFacade(model).generate(limit=3)
        assert len(result) == 3

    def test_returns_empty_list_when_no_schedules(self) -> None:
        model = _make_model(schedules=[])
        result = SchedulerFacade(model).generate(limit=10)
        assert result == []

    def test_limit_is_written_to_config(self) -> None:
        model = _make_model()
        SchedulerFacade(model).generate(limit=42)
        assert model.config_model.config.limit == 42

    def test_generate_schedules_called_with_limit(self) -> None:
        model = _make_model()
        SchedulerFacade(model).generate(limit=7)
        model.generate_schedules.assert_called_once_with(limit=7)


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------

class TestSchedulerFacadeErrors:
    def test_scheduler_exception_propagates(self) -> None:
        model = _make_model()
        model.generate_schedules.side_effect = ValueError("bad config")
        with pytest.raises(ValueError, match="bad config"):
            SchedulerFacade(model).generate(limit=1)

    def test_progress_callback_called_before_exception(self) -> None:
        """Callback should have fired at least the initial 0% before error."""
        model = _make_model()
        model.generate_schedules.side_effect = RuntimeError("boom")
        seen: list[int] = []
        with pytest.raises(RuntimeError):
            SchedulerFacade(model).generate(
                limit=1,
                progress_callback=lambda p, _: seen.append(p),
            )
        assert 0 in seen