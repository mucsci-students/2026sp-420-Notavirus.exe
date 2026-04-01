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
import json
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


# ================================================================
# TESTS: _build_dummy_course
# ================================================================


def test_build_dummy_course_empty_string(scheduler_model):
    course = scheduler_model._build_dummy_course("")
    assert course.course_id == "UNKNOWN"
    assert course.section == 1
    assert course.labs == []
    assert course.faculties == []


def test_build_dummy_course_no_section(scheduler_model):
    course = scheduler_model._build_dummy_course("CS101")
    assert course.course_id == "CS101"
    assert course.section == 1


def test_build_dummy_course_with_section(scheduler_model):
    course = scheduler_model._build_dummy_course(
        "CS101.2", faculty="Dr. Smith", lab="L1"
    )
    assert course.course_id == "CS101"
    assert course.section == 2
    assert "L1" in course.labs
    assert "Dr. Smith" in course.faculties


def test_build_dummy_course_invalid_section(scheduler_model):
    course = scheduler_model._build_dummy_course("CS101.A")
    assert course.course_id == "CS101"
    assert course.section == 1


# ================================================================
# TESTS: _build_time_instance
# ================================================================


def test_build_time_instance_valid(scheduler_model):
    t_dict = {"day": 1, "start": 540, "duration": 50}
    time_instance = scheduler_model._build_time_instance(t_dict)
    assert time_instance.day.value == 1
    assert time_instance.start.value == 540
    assert time_instance.duration.value == 50


def test_build_time_instance_invalid_raises_keyerror(scheduler_model):
    with pytest.raises(KeyError):
        scheduler_model._build_time_instance({"day": 1, "start": 540})


# ================================================================
# TESTS: import/export CSV
# ================================================================


def test_import_csv_empty(scheduler_model):
    schedules = scheduler_model.import_from_csv(b"")
    assert schedules == []


def test_export_import_csv(scheduler_model):
    csv_bytes = b"CS101.1,Dr. Smith,Room A,None,MON 09:00-09:50\n\nCS102.1,Dr. Jones,Room B,L1,TUE 10:00-11:00,WED 10:00-11:00^\n"
    schedules = scheduler_model.import_from_csv(csv_bytes)
    assert len(schedules) == 2
    assert len(schedules[0]) == 1
    assert schedules[0][0].course.course_id == "CS101"
    assert schedules[0][0].faculty == "Dr. Smith"
    assert schedules[0][0].room == "Room A"
    assert schedules[0][0].lab is None

    assert len(schedules[1]) == 1
    assert schedules[1][0].course.course_id == "CS102"
    assert schedules[1][0].lab == "L1"
    assert schedules[1][0].time.lab_index == 1

    exported = scheduler_model.export_to_csv(schedules)

    exported_str = exported.decode("utf-8")
    assert "CS101" in exported_str
    assert "09:00-09:50" in exported_str


def test_import_csv_invalid_format_raises(scheduler_model):
    with pytest.raises(IndexError):
        scheduler_model.import_from_csv(b"CS101,Dr. Smith")


# ================================================================
# TESTS: import/export JSON
# ================================================================


def test_import_json_empty(scheduler_model):
    schedules = scheduler_model.import_from_json(b"[]")
    assert schedules == []


def test_import_json_exception(scheduler_model):
    with pytest.raises(json.JSONDecodeError):
        scheduler_model.import_from_json(b"invalid json")


def test_export_json_uses_as_dict(scheduler_model):
    mock_course = MagicMock()
    mock_course.as_dict.return_value = {"mock": "data"}

    exported = scheduler_model.export_to_json([[mock_course]])
    assert b'"mock": "data"' in exported


def test_export_json_uses_model_dump(scheduler_model):
    mock_course = MagicMock()
    del mock_course.as_dict
    mock_course.model_dump.return_value = {"mock": "dump"}

    exported = scheduler_model.export_to_json([[mock_course]])
    assert b'"mock": "dump"' in exported


def test_import_from_json_valid(scheduler_model):
    json_data = [
        [
            {
                "course_str": "CS101.1",
                "faculty": "Dr. Smith",
                "room": "Room A",
                "lab": None,
                "lab_index": None,
                "times": [{"day": 1, "start": 540, "duration": 50}],
            }
        ]
    ]
    json_bytes = json.dumps(json_data).encode("utf-8")

    schedules = scheduler_model.import_from_json(json_bytes)
    assert len(schedules) == 1
    assert len(schedules[0]) == 1
    assert schedules[0][0].course.course_id == "CS101"
    assert schedules[0][0].room == "Room A"
    assert schedules[0][0].faculty == "Dr. Smith"
