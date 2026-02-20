# tests for delete lab

import pytest
import shutil
from unittest.mock import patch
from scheduler import load_config_from_file
from scheduler.config import CombinedConfig
from lab import deleteLab_json, deleteLab_input

TEST_CONFIG = "tests/testdeletelab.json"

@pytest.fixture
def config_path(tmp_path):
    """Create a temporary copy of the test config file."""
    temp_config = str(tmp_path / "testdeletelab.json")
    shutil.copy(TEST_CONFIG, temp_config)
    return temp_config

@pytest.fixture
def config(config_path):
    """Load the config from the temporary file."""
    return load_config_from_file(CombinedConfig, config_path)


def test_delete_existing_lab(config, config_path):
    """Scenario 1: Delete a lab that exists."""
    # Verify lab exists before deletion
    assert "Linux" in config.config.labs
    
    deleteLab_json("Linux", config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    assert "Linux" not in updated.config.labs


def test_delete_lab_removes_from_courses(config, config_path):
    """Deleting a lab removes it from all courses that have it."""
    # Verify lab is in courses before deletion
    cmsc161 = next(c for c in config.config.courses if c.course_id == "CMSC 161")
    cmsc162 = next(c for c in config.config.courses if c.course_id == "CMSC 162")
    assert "Linux" in cmsc161.lab
    assert "Linux" in cmsc162.lab
    
    deleteLab_json("Linux", config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    cmsc161_updated = next(c for c in updated.config.courses if c.course_id == "CMSC 161")
    cmsc162_updated = next(c for c in updated.config.courses if c.course_id == "CMSC 162")
    assert "Linux" not in cmsc161_updated.lab
    assert "Linux" not in cmsc162_updated.lab


def test_delete_lab_removes_from_faculty_preferences(config, config_path):
    """Deleting a lab removes it from all faculty preferences."""
    # Verify lab is in faculty preferences before deletion
    zoppetti = next(f for f in config.config.faculty if f.name == "Zoppetti")
    brooks = next(f for f in config.config.faculty if f.name == "Brooks")
    assert "Mac" in zoppetti.lab_preferences
    assert "Mac" in brooks.lab_preferences
    
    deleteLab_json("Mac", config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    zoppetti_updated = next(f for f in updated.config.faculty if f.name == "Zoppetti")
    brooks_updated = next(f for f in updated.config.faculty if f.name == "Brooks")
    assert "Mac" not in zoppetti_updated.lab_preferences
    assert "Mac" not in brooks_updated.lab_preferences


def test_delete_lab_preserves_other_labs(config, config_path):
    """Deleting one lab should not affect other labs."""
    assert "Linux" in config.config.labs
    assert "Mac" in config.config.labs
    assert "Windows" in config.config.labs
    
    deleteLab_json("Windows", config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    assert "Linux" in updated.config.labs
    assert "Mac" in updated.config.labs
    assert "Windows" not in updated.config.labs


def test_delete_lab_with_input_valid_selection(config, config_path):
    """Scenario 1: User selects a valid lab and confirms deletion."""
    # List position: 1 = Linux, 2 = Mac, 3 = Windows
    with patch("builtins.input", side_effect=["1", "y"]):
        deleteLab_input(config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    assert "Linux" not in updated.config.labs


def test_delete_lab_with_input_user_cancels(config, config_path):
    """Scenario 2: User selects a lab but cancels confirmation."""
    with patch("builtins.input", side_effect=["2", "n"]):
        deleteLab_input(config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    assert "Mac" in updated.config.labs


def test_delete_lab_with_input_invalid_number_then_valid(config, config_path):
    """Scenario 3: User enters invalid number, then valid number."""
    with patch("builtins.input", side_effect=["0", "99", "1", "y"]):
        deleteLab_input(config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    assert "Linux" not in updated.config.labs


def test_delete_lab_with_input_quit_option(config, config_path):
    """Scenario 4: User quits with -1."""
    with patch("builtins.input", side_effect=["-1"]):
        deleteLab_input(config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    # All labs should still exist
    assert "Linux" in updated.config.labs
    assert "Mac" in updated.config.labs
    assert "Windows" in updated.config.labs


def test_delete_lab_with_input_out_of_range(config, config_path):
    """Scenario 5: User enters number out of range."""
    with patch("builtins.input", side_effect=["5", "2", "y"]):
        deleteLab_input(config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    assert "Mac" not in updated.config.labs


def test_delete_lab_only_removes_specified_lab(config, config_path):
    """Only the specified lab should be removed from courses."""
    cmsc162 = next(c for c in config.config.courses if c.course_id == "CMSC 162")
    # CMSC 162 has both Linux and Mac
    assert "Linux" in cmsc162.lab and "Mac" in cmsc162.lab
    
    deleteLab_json("Linux", config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    cmsc162_updated = next(c for c in updated.config.courses if c.course_id == "CMSC 162")
    # Linux should be removed but Mac should remain
    assert "Linux" not in cmsc162_updated.lab
    assert "Mac" in cmsc162_updated.lab


def test_delete_lab_courses_without_lab_unchanged(config, config_path):
    """Courses without the deleted lab should remain unchanged."""
    cmsc140 = next(c for c in config.config.courses if c.course_id == "CMSC 140")
    # CMSC 140 has no labs
    assert len(cmsc140.lab) == 0
    
    deleteLab_json("Linux", config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    cmsc140_updated = next(c for c in updated.config.courses if c.course_id == "CMSC 140")
    # CMSC 140 should still have no labs
    assert len(cmsc140_updated.lab) == 0


def test_delete_lab_faculty_preferences_preserved(config, config_path):
    """Faculty preferences for other labs should remain when one lab is deleted."""
    zoppetti = next(f for f in config.config.faculty if f.name == "Zoppetti")
    initial_linux_pref = zoppetti.lab_preferences.get("Linux")
    initial_windows_pref = zoppetti.lab_preferences.get("Windows")
    
    # Delete Mac lab
    deleteLab_json("Mac", config, config_path)
    
    updated = load_config_from_file(CombinedConfig, config_path)
    zoppetti_updated = next(f for f in updated.config.faculty if f.name == "Zoppetti")
    # Other preferences should remain unchanged
    assert zoppetti_updated.lab_preferences.get("Linux") == initial_linux_pref
    assert zoppetti_updated.lab_preferences.get("Windows") == initial_windows_pref
    assert "Mac" not in zoppetti_updated.lab_preferences
