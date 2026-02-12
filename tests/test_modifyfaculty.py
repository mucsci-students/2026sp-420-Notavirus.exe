# tests for modify faculty

import pytest
import shutil
from unittest.mock import patch
from scheduler import load_config_from_file
from scheduler.config import CombinedConfig
from faculty import modifyFaculty

TEST_CONFIG = "tests/testmodifyfaculty.json"

@pytest.fixture
def config_path(tmp_path):
    temp_config = str(tmp_path / "testmodifyfaculty.json")
    shutil.copy(TEST_CONFIG, temp_config)
    return temp_config

@pytest.fixture
def config(config_path):
    return load_config_from_file(CombinedConfig, config_path)


def test_modify_max_credits(config, config_path):
    with patch("builtins.input", side_effect=["Yang", "2", "14"]):
        modifyFaculty(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.maximum_credits == 14


def test_modify_min_credits(config, config_path):
    with patch("builtins.input", side_effect=["Yang", "3", "8"]):
        modifyFaculty(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.minimum_credits == 8


def test_modify_position_to_adjunct(config, config_path):
    with patch("builtins.input", side_effect=["Yang", "1", "n"]):
        modifyFaculty(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.maximum_credits == 4
    assert yang.unique_course_limit == 1
    assert yang.minimum_credits <= 4


def test_modify_position_to_fulltime(config, config_path):
    with patch("builtins.input", side_effect=["Yang", "1", "n"]):
        modifyFaculty(config, config_path)
    config = load_config_from_file(CombinedConfig, config_path)
    with patch("builtins.input", side_effect=["Yang", "1", "y"]):
        modifyFaculty(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.maximum_credits == 12
    assert yang.unique_course_limit == 2

def test_modify_max_days(config, config_path):
    with patch("builtins.input", side_effect=["Yang", "5", "3"]):
        modifyFaculty(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.maximum_days == 3


def test_modify_faculty_not_found(config, config_path, capsys):
    with patch("builtins.input", side_effect=["Nobody"]):
        modifyFaculty(config, config_path)
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower() or "No faculty" in captured.out


def test_modify_canceled(config, config_path):
    with patch("builtins.input", side_effect=["Yang", "10"]):
        modifyFaculty(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.maximum_credits == 12

def test_empty_name_reprompts(config, config_path, capsys):
    """Empty name should re-prompt until valid name is entered."""
    with patch("builtins.input", side_effect=["", "", "Yang", "10"]):
        modifyFaculty(config, config_path)

    captured = capsys.readouterr()
    assert "Modification canceled" in captured.out


def test_negative_max_days_reprompts(config, config_path):
    """Negative max days should re-prompt until valid value entered."""
    with patch("builtins.input", side_effect=["Yang", "5", "-1", "3"]):
        modifyFaculty(config, config_path)

    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.maximum_days == 3


def test_end_time_before_start_time_reprompts(config, config_path):
    """End time before start time should re-prompt until valid times entered."""
    with patch("builtins.input", side_effect=[
        "Yang",   # faculty name
        "6",      # choice 6 - availability times
        "MTWRF",  # days
        "17:00",  # start time (invalid - end is before this)
        "09:00",  # end time (before start, should re-prompt)
        "09:00",  # start time (valid)
        "17:00",  # end time (valid)
        "09:00",  # start for TUE
        "17:00",  # end for TUE
        "09:00",  # start for WED
        "17:00",  # end for WED
        "09:00",  # start for THU
        "17:00",  # end for THU
        "09:00",  # start for FRI
        "17:00",  # end for FRI
    ]):
        modifyFaculty(config, config_path)

    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert "MON" in yang.times


def test_clear_course_preferences(config, config_path):
    """Entering nothing for preferences should save empty preferences."""
    with patch("builtins.input", side_effect=["Yang", "7", ""]):
        modifyFaculty(config, config_path)

    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.course_preferences == {}


def test_max_days_lower_than_mandatory_days(config, config_path, capsys):
    """Setting max days lower than mandatory days count should fail."""
    # Yang has 1 mandatory day (WED), so setting max_days to 0 should fail
    with patch("builtins.input", side_effect=["Yang", "5", "0"]):
        modifyFaculty(config, config_path)

    captured = capsys.readouterr()
    assert "validation error" in captured.out.lower() or "Failed" in captured.out

    # Verify max days was not changed
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.maximum_days == 4