# tests/conftest.py
"""
Shared pytest fixtures for all test files.

This file contains fixtures that are used across multiple test modules.
Pytest automatically discovers and makes these fixtures available to all tests.
"""

import pytest
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.faculty_model import FacultyModel
from models.course_model import CourseModel
from models.conflict_model import ConflictModel
from models.lab_model import LabModel
from models.room_model import RoomModel


# ================================================================
# CONFIGURATION FIXTURES
# ================================================================

# Test configuration files
TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_copy.json"


@pytest.fixture
def test_config():
    """
    Create a fresh copy of example.json for each test.
    
    This fixture ensures each test gets a clean copy of the configuration
    file, preventing tests from interfering with each other.
    
    Yields:
        str: Path to test configuration file
    
    Cleanup:
        Deletes the test copy after the test completes
    """
    # Setup: Copy example.json to test_copy.json
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    
    # Provide path to test
    yield TEST_COPY_CONFIG
    
    # Cleanup: Delete test copy
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def config_model(test_config):
    """
    Create a ConfigModel with test configuration.
    
    Parameters:
        test_config (str): Path to test config (from test_config fixture)
    
    Returns:
        ConfigModel: Initialized config model with test data
    """
    return ConfigModel(test_config)


# ================================================================
# MODEL FIXTURES
# ================================================================

@pytest.fixture
def faculty_model(config_model):
    """
    Create a FacultyModel with test configuration.
    
    Parameters:
        config_model (ConfigModel): Shared config model fixture
    
    Returns:
        FacultyModel: Initialized faculty model
    """
    return FacultyModel(config_model)


@pytest.fixture
def course_model(config_model):
    """
    Create a CourseModel with test configuration.
    
    Parameters:
        config_model (ConfigModel): Shared config model fixture
    
    Returns:
        CourseModel: Initialized course model
    """
    return CourseModel(config_model)


@pytest.fixture
def conflict_model(config_model):
    """
    Create a ConflictModel with test configuration.
    
    Parameters:
        config_model (ConfigModel): Shared config model fixture
    
    Returns:
        ConflictModel: Initialized conflict model
    """
    return ConflictModel(config_model)


@pytest.fixture
def lab_model(config_model):
    """
    Create a LabModel with test configuration.
    
    Parameters:
        config_model (ConfigModel): Shared config model fixture
    
    Returns:
        LabModel: Initialized lab model
    """
    return LabModel(config_model)


@pytest.fixture
def room_model(config_model):
    """
    Create a RoomModel with test configuration.
    
    Parameters:
        config_model (ConfigModel): Shared config model fixture
    
    Returns:
        RoomModel: Initialized room model
    """
    return RoomModel(config_model)


# ================================================================
# PYTEST CONFIGURATION
# ================================================================

def pytest_configure(config):
    """
    Pytest configuration hook.
    
    Add custom markers here if needed.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


# ================================================================
# HELPER FIXTURES (Optional - uncomment if needed)
# ================================================================

# @pytest.fixture
# def sample_faculty_data():
#     """
#     Provide sample faculty data for testing.
#     
#     Returns:
#         dict: Sample faculty configuration data
#     """
#     return {
#         'name': 'Test Faculty',
#         'is_full_time': True,
#         'days': ['M', 'W', 'F'],
#         'course_preferences': {'CMSC 161': 5}
#     }


# @pytest.fixture
# def sample_course_data():
#     """
#     Provide sample course data for testing.
#     
#     Returns:
#         dict: Sample course configuration data
#     """
#     return {
#         'course_id': 'TEST 101',
#         'credits': 3,
#         'rooms': ['Roddy 140'],
#         'labs': ['Linux'],
#         'faculty': ['Hardy']
#     }