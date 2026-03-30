# tests/test_models/test_scheduler_model.py
"""
Unit tests for SchedulerModel limit override functionality.

Tests cover:
- Initialization
- generate_schedules with no limit (config value unchanged)
- generate_schedules with limit override (updates config.limit in memory)
- Override does not write back to the config file
- count_possible_schedules behaviour
"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from models.config_model import ConfigModel
from models.scheduler_model import SchedulerModel


# ================================================================
# PYTEST FIXTURES
# ================================================================

TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_scheduler_copy.json"


@pytest.fixture
def test_config():
    """
    Create a fresh copy of example.json for each test.

    Yields:
        str: Path to test configuration file
    """
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def config_model(test_config):
    """
    Create a ConfigModel from the test config copy.

    Parameters:
        test_config (str): Path to test config fixture

    Returns:
        ConfigModel: Initialized config model
    """
    return ConfigModel(test_config)


@pytest.fixture
def scheduler_model(config_model):
    """
    Create a SchedulerModel with the test config model.

    Parameters:
        config_model (ConfigModel): Shared config model fixture

    Returns:
        SchedulerModel: Initialized scheduler model
    """
    return SchedulerModel(config_model)


# ================================================================
# TESTS: Initialization
# ================================================================


def test_scheduler_model_initialization(scheduler_model, config_model):
    """
    Test that SchedulerModel initializes with the correct config_model reference.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
        config_model (ConfigModel): Config model fixture
    """
    assert scheduler_model is not None
    assert scheduler_model.config_model is config_model


def test_scheduler_model_config_has_limit(scheduler_model):
    """
    Test that the config loaded from example.json has a limit field.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    assert hasattr(scheduler_model.config_model.config, "limit")
    assert scheduler_model.config_model.config.limit == 100


# ================================================================
# TESTS: generate_schedules — no limit argument
# ================================================================


def test_generate_schedules_no_limit_leaves_config_unchanged(scheduler_model):
    """
    Test that calling generate_schedules without a limit does not modify config.limit.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    original_limit = scheduler_model.config_model.config.limit

    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules())

    assert scheduler_model.config_model.config.limit == original_limit


def test_generate_schedules_no_limit_calls_scheduler_with_config(scheduler_model):
    """
    Test that generate_schedules passes the config object to Scheduler even with no limit.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules())

    MockScheduler.assert_called_once_with(scheduler_model.config_model.config)


# ================================================================
# TESTS: generate_schedules — with limit override
# ================================================================


def test_generate_schedules_limit_override_updates_config(scheduler_model):
    """
    Test that passing a limit to generate_schedules overrides config.limit in memory.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules(limit=42))

    assert scheduler_model.config_model.config.limit == 42


def test_generate_schedules_limit_one_accepted(scheduler_model):
    """
    Test that a limit of 1 is accepted and applied.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules(limit=1))

    assert scheduler_model.config_model.config.limit == 1


def test_generate_schedules_limit_large_value(scheduler_model):
    """
    Test that a large limit value is accepted and applied.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules(limit=9999))

    assert scheduler_model.config_model.config.limit == 9999


def test_generate_schedules_multiple_overrides_uses_latest(scheduler_model):
    """
    Test that each call with a new limit updates config.limit to the most recent value.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules(limit=10))

    assert scheduler_model.config_model.config.limit == 10

    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules(limit=50))

    assert scheduler_model.config_model.config.limit == 50


def test_generate_schedules_override_does_not_write_to_file(
    scheduler_model, test_config
):
    """
    Test that overriding the limit in memory does not save back to the JSON file.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
        test_config (str): Path to the test config file
    """
    original_limit = scheduler_model.config_model.config.limit

    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules(limit=999))

    # Reload from disk and confirm the file was not modified
    reloaded = ConfigModel(test_config)
    assert reloaded.config.limit == original_limit


def test_generate_schedules_passes_config_to_scheduler(scheduler_model):
    """
    Test that generate_schedules passes config to Scheduler after applying the override.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        list(scheduler_model.generate_schedules(limit=5))

    MockScheduler.assert_called_once_with(scheduler_model.config_model.config)


def test_generate_schedules_returns_scheduler_results(scheduler_model):
    """
    Test that generate_schedules returns what the Scheduler yields.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    fake_schedules = [MagicMock(name="s1"), MagicMock(name="s2"), MagicMock(name="s3")]

    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter(fake_schedules)
        result = list(scheduler_model.generate_schedules(limit=3))

    assert result == fake_schedules


# ================================================================
# TESTS: count_possible_schedules
# ================================================================


def test_count_possible_schedules_returns_zero_when_empty(scheduler_model):
    """
    Test count_possible_schedules returns 0 when no schedules are produced.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter([])
        count = scheduler_model.count_possible_schedules()

    assert count == 0


def test_count_possible_schedules_counts_correctly(scheduler_model):
    """
    Test count_possible_schedules returns the correct count.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    fake_schedules = [MagicMock() for _ in range(7)]

    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = iter(fake_schedules)
        count = scheduler_model.count_possible_schedules(max_check=10)

    assert count == 7


def test_count_possible_schedules_respects_max_check(scheduler_model):
    """
    Test count_possible_schedules passes max_check as the limit to the Scheduler,
    so the Scheduler (not this method) caps the results.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """
    max_check = 3

    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        # Real Scheduler would stop at max_check; mock reflects that
        MockScheduler.return_value.get_models.return_value = iter(
            [MagicMock() for _ in range(max_check)]
        )
        count = scheduler_model.count_possible_schedules(max_check=max_check)

    assert count == max_check
    assert scheduler_model.config_model.config.limit == max_check


def test_count_possible_schedules_handles_exception_gracefully(scheduler_model):
    """
    Test count_possible_schedules returns partial count if the generator raises.

    Parameters:
        scheduler_model (SchedulerModel): Scheduler model fixture
    """

    def _failing_gen():
        yield MagicMock()
        yield MagicMock()
        raise RuntimeError("scheduler error")

    with patch("models.scheduler_model.Scheduler") as MockScheduler:
        MockScheduler.return_value.get_models.return_value = _failing_gen()
        count = scheduler_model.count_possible_schedules()

    assert count == 2
