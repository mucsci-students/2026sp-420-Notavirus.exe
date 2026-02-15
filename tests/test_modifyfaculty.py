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
        "M",      # only Monday
        "12:00",  # start time
        "10:00",  # end time before start - should re-prompt
        "09:00",  # valid start time
        "17:00",  # valid end time
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
    with patch("builtins.input", side_effect=["Yang", "5", "0"]):
        modifyFaculty(config, config_path)
    captured = capsys.readouterr()
    assert "validation error" in captured.out.lower() or "Failed" in captured.out
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.maximum_days == 4


def test_no_availability(config, config_path):
    """Typing 'none' should set all days to empty."""
    with patch("builtins.input", side_effect=["Yang", "6", "none"]):
        modifyFaculty(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert all(yang.times[day] == [] for day in yang.times)


def test_default_times(config, config_path):
    """Pressing Enter for times should default to 00:00-23:59."""
    with patch("builtins.input", side_effect=[
        "Yang",  # faculty name
        "6",     # choice 6
        "MW",    # Monday and Wednesday (WED is mandatory for Yang)
        "",      # default start 00:00 for MON
        "",      # default end 23:59 for MON
        "",      # default start 00:00 for WED
        "",      # default end 23:59 for WED
    ]):
        modifyFaculty(config, config_path)
    updated = load_config_from_file(CombinedConfig, config_path)
    yang = next(f for f in updated.config.faculty if f.name == "Yang")
    assert yang.times["MON"][0].start == "00:00"
    assert yang.times["MON"][0].end == "23:59"