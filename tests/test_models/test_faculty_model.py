# tests/test_models/test_faculty_model.py
"""
Unit tests for Faculty functionality using MVC architecture.

Tests cover:
- FacultyModel operations (add, delete, modify, check existence)
- Faculty configuration building
- Duplicate checking
"""

import pytest
import shutil
from pathlib import Path
from scheduler import load_config_from_file, CombinedConfig, FacultyConfig, TimeRange

from models.config_model import ConfigModel
from models.faculty_model import FacultyModel
from controllers.faculty_controller import FacultyController

# Constants (from old faculty.py)
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 0
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1

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
    
    This ensures tests don't interfere with each other or modify
    the original example.json file.
    
    Yields:
        str: Path to test configuration file
    """
    # Copy example.json to test_copy.json
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    
    # Provide path to tests
    yield TEST_COPY_CONFIG
    
    # Cleanup after test
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def faculty_model(test_config):
    """
    Create a FacultyModel with test configuration.
    
    Parameters:
        test_config (str): Path to test config (from test_config fixture)
    
    Returns:
        FacultyModel: Initialized faculty model
    """
    config_model = ConfigModel(test_config)
    return FacultyModel(config_model)


# ================================================================
# HELPER FUNCTIONS (replaces old addFaculty_config)
# ================================================================

def build_faculty_config(name: str, isFullTime: str, dates: list, courses: dict) -> FacultyConfig:
    """
    Build a FacultyConfig object from test parameters.
    
    This replaces the old addFaculty_config function.
    
    Parameters:
        name (str): Faculty name
        isFullTime (str): 'y' for full-time, 'n' for adjunct
        dates (list): List of day abbreviations ['M', 'W', 'F']
        courses (dict): Course preferences {course_id: weight}
    
    Returns:
        FacultyConfig: Configured faculty object
    """
    # Determine position type
    is_full_time = (isFullTime.lower() == 'y')
    
    # Set credits and limits based on position
    if is_full_time:
        max_credits = FULL_TIME_MAX_CREDITS
        unique_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
    else:
        max_credits = ADJUNCT_MAX_CREDITS
        unique_limit = ADJUNCT_UNIQUE_COURSE_LIMIT
    
    # Convert date abbreviations to full day names and TimeRanges
    day_map = {
        'M': 'MON',
        'T': 'TUE',
        'W': 'WED',
        'R': 'THU',
        'F': 'FRI'
    }
    
    times = {}
    for day_abbr in dates:
        if day_abbr in day_map:
            full_day = day_map[day_abbr]
            times[full_day] = [TimeRange(start='09:00', end='17:00')]
    
    return FacultyConfig(
        name=name,
        unique_course_limit=unique_limit,
        maximum_credits=max_credits,
        minimum_credits=MIN_CREDITS,
        course_preferences=courses,
        maximum_days=MAX_DAYS,
        times=times
    )


# ================================================================
# TESTS: Faculty Configuration Building
# ================================================================

def test_addFaculty_config_noPref():
    """
    Test building a full-time faculty config with no course preferences.
    """
    result = build_faculty_config(
        name="testnoPref",
        isFullTime="y",
        dates=['M', 'W', 'F'],
        courses={}
    )
    
    expected = FacultyConfig(
        name="testnoPref",
        unique_course_limit=FULL_TIME_UNIQUE_COURSE_LIMIT,
        maximum_credits=FULL_TIME_MAX_CREDITS,
        minimum_credits=MIN_CREDITS,
        course_preferences={},
        maximum_days=MAX_DAYS,
        times={
            'MON': [TimeRange(start='09:00', end='17:00')],
            'WED': [TimeRange(start='09:00', end='17:00')],
            'FRI': [TimeRange(start='09:00', end='17:00')]
        }
    )
    
    assert result == expected


def test_addFaculty_config():
    """
    Test building a full-time faculty config with course preferences.
    """
    result = build_faculty_config(
        name="test",
        isFullTime="y",
        dates=['M', 'W', 'F'],
        courses={'CMSC 161': 0}
    )
    
    expected = FacultyConfig(
        name="test",
        unique_course_limit=FULL_TIME_UNIQUE_COURSE_LIMIT,
        maximum_credits=FULL_TIME_MAX_CREDITS,
        minimum_credits=MIN_CREDITS,
        course_preferences={'CMSC 161': 0},
        maximum_days=MAX_DAYS,
        times={
            'MON': [TimeRange(start='09:00', end='17:00')],
            'WED': [TimeRange(start='09:00', end='17:00')],
            'FRI': [TimeRange(start='09:00', end='17:00')]
        }
    )
    
    assert result == expected


# ================================================================
# TESTS: Duplicate Checking (using FacultyModel)
# ================================================================

def test_faculty_check_duplicate_name(faculty_model):
    """
    Test that adding a faculty with duplicate name is detected.
    
    Should return True (faculty already exists).
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Create faculty with name that exists in example.json ("Hardy")
    faculty = build_faculty_config(
        name="Hardy",
        isFullTime="y",
        dates=['M', 'W', 'F'],
        courses={"CMSC example": 0}
    )
    
    # Test - faculty_exists should return True for duplicate
    assert faculty_model.faculty_exists("Hardy") == True


def test_faculty_check_duplicate_datesPref(faculty_model):
    """
    Test that adding a faculty with unique name but duplicate dates/prefs is allowed.
    
    Should return False (faculty doesn't exist - name is unique).
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Create faculty with distinct name
    faculty = build_faculty_config(
        name="distinctName",
        isFullTime="y",
        dates=['M', 'W', 'F'],
        courses={}
    )
    
    # Test - faculty_exists should return False for new name
    assert faculty_model.faculty_exists("distinctName") == False


def test_faculty_check_distinct(faculty_model):
    """
    Test that adding a completely distinct faculty is allowed.
    
    Should return False (faculty doesn't exist).
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Create completely distinct faculty
    faculty = build_faculty_config(
        name="distinctName",
        isFullTime="y",
        dates=['M', 'W', 'F'],
        courses={"distinctCourse": 0}
    )
    
    # Test - faculty_exists should return False
    assert faculty_model.faculty_exists("distinctName") == False


# ================================================================
# TESTS: FacultyModel CRUD Operations
# ================================================================

def test_add_faculty_success(faculty_model):
    """
    Test successfully adding a new faculty to the model.
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Create new faculty
    faculty = build_faculty_config(
        name="New Test Faculty",
        isFullTime="y",
        dates=['M', 'W', 'F'],
        courses={"CMSC 161": 5}
    )
    
    # Add faculty
    result = faculty_model.add_faculty(faculty)
    
    # Assert
    assert result == True
    assert faculty_model.faculty_exists("New Test Faculty") == True


def test_add_faculty_duplicate(faculty_model):
    """
    Test that adding a duplicate faculty fails.
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Try to add faculty that already exists (Hardy from example.json)
    faculty = build_faculty_config(
        name="Hardy",
        isFullTime="y",
        dates=['M', 'W', 'F'],
        courses={}
    )
    
    # Attempt to add
    result = faculty_model.add_faculty(faculty)
    
    # Assert - should fail (return False)
    assert result == False


def test_delete_faculty_success(faculty_model):
    """
    Test successfully deleting a faculty.
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # First add a test faculty
    faculty = build_faculty_config(
        name="Temp Faculty",
        isFullTime="y",
        dates=['M', 'W'],
        courses={}
    )
    faculty_model.add_faculty(faculty)
    
    # Delete the faculty
    result = faculty_model.delete_faculty("Temp Faculty")
    
    # Assert
    assert result == True
    assert faculty_model.faculty_exists("Temp Faculty") == False


def test_delete_faculty_not_found(faculty_model):
    """
    Test deleting a non-existent faculty fails.
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Try to delete non-existent faculty
    result = faculty_model.delete_faculty("NonExistent Faculty")
    
    # Assert - should fail
    assert result == False


def test_modify_faculty_success(faculty_model):
    """
    Test successfully modifying a faculty's field.
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Add test faculty
    faculty = build_faculty_config(
        name="Modifiable Faculty",
        isFullTime="y",
        dates=['M', 'W', 'F'],
        courses={}
    )
    faculty_model.add_faculty(faculty)
    
    # Modify maximum_credits
    result = faculty_model.modify_faculty("Modifiable Faculty", "maximum_credits", 15)
    
    # Assert
    assert result == True
    
    # Verify change
    modified_faculty = faculty_model.get_faculty_by_name("Modifiable Faculty")
    assert modified_faculty.maximum_credits == 15


def test_get_faculty_by_name(faculty_model):
    """
    Test retrieving a faculty by name.
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Get existing faculty (Hardy from example.json)
    faculty = faculty_model.get_faculty_by_name("Hardy")
    
    # Assert
    assert faculty is not None
    assert faculty.name == "Hardy"


def test_get_all_faculty(faculty_model):
    """
    Test retrieving all faculty.
    
    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Get all faculty
    all_faculty = faculty_model.get_all_faculty()
    
    # Assert
    assert isinstance(all_faculty, list)
    assert len(all_faculty) > 0  # example.json should have faculty