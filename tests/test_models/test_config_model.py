# tests/test_models/test_config_model.py
"""
Unit tests for ConfigModel.

Tests cover:
- Loading configuration from file
- Saving configuration
- Reloading configuration
- Helper getter methods
"""

import pytest
import shutil
from pathlib import Path

from models.config_model import ConfigModel

# Test configuration
TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_copy.json"


# ================================================================
# PYTEST FIXTURES
# ================================================================

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


# ================================================================
# TESTS: Initialization
# ================================================================

def test_config_model_initialization(test_config):
    """
    Test that ConfigModel initializes correctly.
    
    Parameters:
        test_config (str): Path to test config fixture
    """
    config_model = ConfigModel(test_config)
    
    assert config_model is not None
    assert config_model.config is not None
    assert config_model.config_path == test_config


def test_config_model_loads_valid_config(test_config):
    """
    Test that ConfigModel loads a valid configuration.
    
    Parameters:
        test_config (str): Path to test config fixture
    """
    config_model = ConfigModel(test_config)
    
    # Verify config has expected structure
    assert hasattr(config_model.config, 'config')
    assert hasattr(config_model.config.config, 'courses')
    assert hasattr(config_model.config.config, 'faculty')
    assert hasattr(config_model.config.config, 'rooms')
    assert hasattr(config_model.config.config, 'labs')


# ================================================================
# TESTS: Save and Reload
# ================================================================

def test_safe_save_success(test_config):
    """
    Test that safe_save successfully saves configuration.
    
    Parameters:
        test_config (str): Path to test config fixture
    """
    config_model = ConfigModel(test_config)
    
    # Modify something
    original_room_count = len(config_model.config.config.rooms)
    config_model.config.config.rooms.append("Test Room")
    
    # Save
    result = config_model.safe_save()
    
    assert result == True
    assert len(config_model.config.config.rooms) == original_room_count + 1


def test_reload_updates_config(test_config):
    """
    Test that reload refreshes the configuration from file.
    
    Parameters:
        test_config (str): Path to test config fixture
    """
    config_model = ConfigModel(test_config)
    
    # Modify and save
    config_model.config.config.rooms.append("Reload Test Room")
    config_model.safe_save()
    
    # Reload
    config_model.reload()
    
    # Verify change persisted
    assert "Reload Test Room" in config_model.config.config.rooms


# ================================================================
# TESTS: Helper Methods
# ================================================================

def test_get_all_courses(test_config):
    """
    Test get_all_courses returns course list.
    
    Parameters:
        test_config (str): Path to test config fixture
    """
    config_model = ConfigModel(test_config)
    
    courses = config_model.get_all_courses()
    
    assert isinstance(courses, list)
    assert len(courses) > 0  # example.json should have courses


def test_get_all_faculty(test_config):
    """
    Test get_all_faculty returns faculty list.
    
    Parameters:
        test_config (str): Path to test config fixture
    """
    config_model = ConfigModel(test_config)
    
    faculty = config_model.get_all_faculty()
    
    assert isinstance(faculty, list)
    assert len(faculty) > 0  # example.json should have faculty


def test_get_all_rooms(test_config):
    """
    Test get_all_rooms returns room list.
    
    Parameters:
        test_config (str): Path to test config fixture
    """
    config_model = ConfigModel(test_config)
    
    rooms = config_model.get_all_rooms()
    
    assert isinstance(rooms, list)
    assert len(rooms) > 0  # example.json should have rooms


def test_get_all_labs(test_config):
    """
    Test get_all_labs returns lab list.
    
    Parameters:
        test_config (str): Path to test config fixture
    """
    config_model = ConfigModel(test_config)
    
    labs = config_model.get_all_labs()
    
    assert isinstance(labs, list)
    assert len(labs) > 0  # example.json should have labs


# ================================================================
# TESTS: Error Handling
# ================================================================

def test_config_model_nonexistent_file():
    """
    Test that ConfigModel handles non-existent files gracefully.
    """
    with pytest.raises(FileNotFoundError):
        ConfigModel("nonexistent_file.json")