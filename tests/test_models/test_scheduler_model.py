# tests/test_models/test_scheduler_model.py
"""
Unit tests for SchedulerModel with optimizer flags.

Tests cover:
- Setting optimizer flags on the config
- Generating schedules with no flags
- Generating schedules with all flags
- Generating schedules with individual flags
"""

import pytest
import shutil
from pathlib import Path
from scheduler import OptimizerFlags

from models.config_model import ConfigModel
from models.scheduler_model import SchedulerModel

TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_copy_scheduler.json"


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def test_config():
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def config_model(test_config):
    return ConfigModel(test_config)


@pytest.fixture
def scheduler_model(config_model):
    return SchedulerModel(config_model)


# ================================================================
# TESTS: Optimizer flags on config
# ================================================================

def test_default_flags_loaded_from_json(scheduler_model):
    """example.json has optimizer_flags set — they should load into config."""
    flags = scheduler_model.config_model.config.optimizer_flags
    assert isinstance(flags, list)
    assert len(flags) > 0


def test_set_no_flags(scheduler_model):
    """Setting an empty flag list is allowed."""
    scheduler_model.config_model.config.optimizer_flags = []
    assert scheduler_model.config_model.config.optimizer_flags == []


def test_set_single_flag(scheduler_model):
    """Setting a single optimizer flag is stored correctly."""
    scheduler_model.config_model.config.optimizer_flags = [OptimizerFlags.FACULTY_COURSE]
    flags = scheduler_model.config_model.config.optimizer_flags
    assert OptimizerFlags.FACULTY_COURSE in flags
    assert len(flags) == 1


def test_set_all_flags(scheduler_model):
    """All five GUI-exposed flags can be set at once."""
    all_flags = [
        OptimizerFlags.FACULTY_COURSE,
        OptimizerFlags.FACULTY_ROOM,
        OptimizerFlags.FACULTY_LAB,
        OptimizerFlags.SAME_ROOM,
        OptimizerFlags.SAME_LAB,
    ]
    scheduler_model.config_model.config.optimizer_flags = all_flags
    stored = scheduler_model.config_model.config.optimizer_flags
    for flag in all_flags:
        assert flag in stored


def test_set_flags_replaces_previous(scheduler_model):
    """Assigning new flags replaces old ones completely."""
    scheduler_model.config_model.config.optimizer_flags = [OptimizerFlags.FACULTY_COURSE]
    scheduler_model.config_model.config.optimizer_flags = [OptimizerFlags.SAME_ROOM]
    flags = scheduler_model.config_model.config.optimizer_flags
    assert OptimizerFlags.SAME_ROOM in flags
    assert OptimizerFlags.FACULTY_COURSE not in flags


# ================================================================
# TESTS: Schedule generation with various flag combinations
# ================================================================

@pytest.mark.slow
def test_generate_with_no_flags(scheduler_model):
    """Schedules can be generated with no optimization flags."""
    scheduler_model.config_model.config.optimizer_flags = []
    schedules = list(scheduler_model.generate_schedules(limit=1))
    assert len(schedules) >= 1


@pytest.mark.slow
def test_generate_with_course_preference_flag(scheduler_model):
    """Schedules can be generated with only course preference optimization."""
    scheduler_model.config_model.config.optimizer_flags = [OptimizerFlags.FACULTY_COURSE]
    schedules = list(scheduler_model.generate_schedules(limit=1))
    assert len(schedules) >= 1


@pytest.mark.slow
def test_generate_with_room_preference_flag(scheduler_model):
    """Schedules can be generated with only room preference optimization."""
    scheduler_model.config_model.config.optimizer_flags = [OptimizerFlags.FACULTY_ROOM]
    schedules = list(scheduler_model.generate_schedules(limit=1))
    assert len(schedules) >= 1


@pytest.mark.slow
def test_generate_with_lab_preference_flag(scheduler_model):
    """Schedules can be generated with only lab preference optimization."""
    scheduler_model.config_model.config.optimizer_flags = [OptimizerFlags.FACULTY_LAB]
    schedules = list(scheduler_model.generate_schedules(limit=1))
    assert len(schedules) >= 1


@pytest.mark.slow
def test_generate_with_all_flags(scheduler_model):
    """Schedules can be generated with all GUI-exposed flags active."""
    scheduler_model.config_model.config.optimizer_flags = [
        OptimizerFlags.FACULTY_COURSE,
        OptimizerFlags.FACULTY_ROOM,
        OptimizerFlags.FACULTY_LAB,
        OptimizerFlags.SAME_ROOM,
        OptimizerFlags.SAME_LAB,
    ]
    schedules = list(scheduler_model.generate_schedules(limit=1))
    assert len(schedules) >= 1


@pytest.mark.slow
def test_generate_respects_limit(scheduler_model):
    """generate_schedules never returns more than the requested limit."""
    scheduler_model.config_model.config.optimizer_flags = []
    schedules = list(scheduler_model.generate_schedules(limit=3))
    assert len(schedules) <= 3


@pytest.mark.slow
def test_generate_returns_non_empty_schedule(scheduler_model):
    """Each generated schedule contains at least one course instance."""
    scheduler_model.config_model.config.optimizer_flags = []
    schedules = list(scheduler_model.generate_schedules(limit=1))
    assert len(schedules) >= 1
    assert len(schedules[0]) > 0
