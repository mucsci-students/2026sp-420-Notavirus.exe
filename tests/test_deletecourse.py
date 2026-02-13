# tests for delete course

import pytest
import shutil
from unittest.mock import patch
from scheduler import load_config_from_file
from scheduler.config import CombinedConfig
from course import deleteCourse

TEST_CONFIG = "tests/testdeletecourse.json"

@pytest.fixture
def config_path(tmp_path):
    temp_config = str(tmp_path / "testdeletecourse.json")
    shutil.copy(TEST_CONFIG, temp_config)
    return temp_config

@pytest.fixture
def config(config_path):
    return load_config_from_file(CombinedConfig, config_path)


def test_delete_existing_course(config, config_path):
    """Scenario 1: Delete a course that exists."""
    with patch("builtins.input", side_effect=["CMSC 162", "y"]):
        deleteCourse(config, config_path)

    updated = load_config_from_file(CombinedConfig, config_path)
    course_ids = [c.course_id for c in updated.config.courses]
    assert "CMSC 162" not in course_ids


def test_delete_course_removes_conflicts(config, config_path):
    """Deleting a course removes it from other courses' conflicts."""
    with patch("builtins.input", side_effect=["CMSC 161", "y"]):
        deleteCourse(config, config_path)

    updated = load_config_from_file(CombinedConfig, config_path)
    cmsc140 = next(c for c in updated.config.courses if c.course_id == "CMSC 140")
    assert "CMSC 161" not in cmsc140.conflicts


def test_delete_course_removes_faculty_preferences(config, config_path):
    """Deleting a course removes it from faculty preferences."""
    with patch("builtins.input", side_effect=["CMSC 161", "y"]):
        deleteCourse(config, config_path)

    updated = load_config_from_file(CombinedConfig, config_path)
    zoppetti = next(f for f in updated.config.faculty if f.name == "Zoppetti")
    assert "CMSC 161" not in zoppetti.course_preferences


def test_delete_course_canceled(config, config_path):
    """Scenario 1: User cancels — no changes made."""
    with patch("builtins.input", side_effect=["CMSC 162", "n"]):
        deleteCourse(config, config_path)

    updated = load_config_from_file(CombinedConfig, config_path)
    course_ids = [c.course_id for c in updated.config.courses]
    assert "CMSC 162" in course_ids


def test_delete_course_not_found(config, config_path, capsys):
    """Scenario 2: Course doesn't exist."""
    with patch("builtins.input", side_effect=["CMSC 999"]):
        deleteCourse(config, config_path)

    captured = capsys.readouterr()
    assert "not found" in captured.out.lower() or "No course" in captured.out