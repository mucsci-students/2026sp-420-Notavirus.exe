# tests for delete conflict

import pytest
import shutil
from unittest.mock import patch
from scheduler import load_config_from_file
from scheduler.config import CombinedConfig
from conflict import deleteConflict

TEST_CONFIG = "tests/testdeleteconflict.json"

@pytest.fixture
def config_path(tmp_path):
    # Copy the test config to a temp location so we don't modify the original
    temp_config = str(tmp_path / "testdeleteconflict.json")
    shutil.copy(TEST_CONFIG, temp_config)
    return temp_config

@pytest.fixture
def config(config_path):
    return load_config_from_file(CombinedConfig, config_path)


def test_delete_existing_conflict(config, config_path):
    """Scenario 1: Delete a conflict that exists."""
    with patch("builtins.input", side_effect=["CMSC 140", "CMSC 161", "y"]):
        deleteConflict(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    cmsc140 = next(c for c in updated.config.courses if c.course_id == "CMSC 140")
    cmsc161 = next(c for c in updated.config.courses if c.course_id == "CMSC 161")
    assert "CMSC 161" not in cmsc140.conflicts
    assert "CMSC 140" not in cmsc161.conflicts

def test_delete_conflict_reversed_order(config, config_path):
    """Scenario 1: Order of input shouldn't matter."""
    with patch("builtins.input", side_effect=["CMSC 161", "CMSC 140", "y"]):
        deleteConflict(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    cmsc140 = next(c for c in updated.config.courses if c.course_id == "CMSC 140")
    cmsc161 = next(c for c in updated.config.courses if c.course_id == "CMSC 161")
    assert "CMSC 161" not in cmsc140.conflicts
    assert "CMSC 140" not in cmsc161.conflicts

def test_delete_conflict_canceled(config, config_path):
    """Scenario 1: User cancels — no changes made."""
    with patch("builtins.input", side_effect=["CMSC 140", "CMSC 161", "n"]):
        deleteConflict(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    cmsc140 = next(c for c in updated.config.courses if c.course_id == "CMSC 140")
    assert "CMSC 161" in cmsc140.conflicts

def test_delete_invalid_course(config, config_path, capsys):
    """Scenario 2: Course doesn't exist — re-prompts then cancels."""
    with patch("builtins.input", side_effect=["CMSC 999", "CMSC 140", "CMSC 161", "n"]):
        deleteConflict(config, config_path)
    captured = capsys.readouterr()
    assert "not a valid course" in captured.out

def test_delete_conflict_does_not_exist(config, config_path, capsys):
    """Scenario 2: Both courses exist but no conflict between them — re-prompts then cancels."""
    with patch("builtins.input", side_effect=["CMSC 140", "CMSC 162", "CMSC 161", "n"]):
        deleteConflict(config, config_path)
    captured = capsys.readouterr()
    assert "No conflict exists" in captured.out

def test_delete_displays_section_labels(config, config_path, capsys):
    """Section labels like CMSC 140.01 should appear in the conflict display."""
    with patch("builtins.input", side_effect=["CMSC 140", "CMSC 161", "n"]):
        deleteConflict(config, config_path)
    captured = capsys.readouterr()
    assert ".01" in captured.out or ".02" in captured.out