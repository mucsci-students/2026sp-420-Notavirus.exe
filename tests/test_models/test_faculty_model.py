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
from scheduler import FacultyConfig, TimeRange

from models.config_model import ConfigModel
from models.faculty_model import FacultyModel

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


def build_faculty_config(
    name: str, isFullTime: str, dates: list, courses: dict
) -> FacultyConfig:
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
    is_full_time = isFullTime.lower() == "y"

    # Set credits and limits based on position
    if is_full_time:
        max_credits = FULL_TIME_MAX_CREDITS
        unique_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
    else:
        max_credits = ADJUNCT_MAX_CREDITS
        unique_limit = ADJUNCT_UNIQUE_COURSE_LIMIT

    # Convert date abbreviations to full day names and TimeRanges
    day_map = {"M": "MON", "T": "TUE", "W": "WED", "R": "THU", "F": "FRI"}

    times = {}
    for day_abbr in dates:
        if day_abbr in day_map:
            full_day = day_map[day_abbr]
            times[full_day] = [TimeRange(start="09:00", end="17:00")]

    return FacultyConfig(
        name=name,
        unique_course_limit=unique_limit,
        maximum_credits=max_credits,
        minimum_credits=MIN_CREDITS,
        course_preferences=courses,
        maximum_days=MAX_DAYS,
        times=times,
    )


# ================================================================
# TESTS: Faculty Configuration Building
# ================================================================


def test_addFaculty_config_noPref():
    """
    Test building a full-time faculty config with no course preferences.
    """
    result = build_faculty_config(
        name="testnoPref", isFullTime="y", dates=["M", "W", "F"], courses={}
    )

    expected = FacultyConfig(
        name="testnoPref",
        unique_course_limit=FULL_TIME_UNIQUE_COURSE_LIMIT,
        maximum_credits=FULL_TIME_MAX_CREDITS,
        minimum_credits=MIN_CREDITS,
        course_preferences={},
        maximum_days=MAX_DAYS,
        times={
            "MON": [TimeRange(start="09:00", end="17:00")],
            "WED": [TimeRange(start="09:00", end="17:00")],
            "FRI": [TimeRange(start="09:00", end="17:00")],
        },
    )

    assert result == expected


def test_addFaculty_config():
    """
    Test building a full-time faculty config with course preferences.
    """
    result = build_faculty_config(
        name="test", isFullTime="y", dates=["M", "W", "F"], courses={"CMSC 161": 0}
    )

    expected = FacultyConfig(
        name="test",
        unique_course_limit=FULL_TIME_UNIQUE_COURSE_LIMIT,
        maximum_credits=FULL_TIME_MAX_CREDITS,
        minimum_credits=MIN_CREDITS,
        course_preferences={"CMSC 161": 0},
        maximum_days=MAX_DAYS,
        times={
            "MON": [TimeRange(start="09:00", end="17:00")],
            "WED": [TimeRange(start="09:00", end="17:00")],
            "FRI": [TimeRange(start="09:00", end="17:00")],
        },
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
    build_faculty_config(
        name="Hardy", isFullTime="y", dates=["M", "W", "F"], courses={"CMSC example": 0}
    )

    # Test - faculty_exists should return True for duplicate
    assert faculty_model.faculty_exists("Hardy")


def test_faculty_check_duplicate_datesPref(faculty_model):
    """
    Test that adding a faculty with unique name but duplicate dates/prefs is allowed.

    Should return False (faculty doesn't exist - name is unique).

    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Create faculty with distinct name
    build_faculty_config(
        name="distinctName", isFullTime="y", dates=["M", "W", "F"], courses={}
    )

    # Test - faculty_exists should return False for new name
    assert not faculty_model.faculty_exists("distinctName")


def test_faculty_check_distinct(faculty_model):
    """
    Test that adding a completely distinct faculty is allowed.

    Should return False (faculty doesn't exist).

    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Create completely distinct faculty
    build_faculty_config(
        name="distinctName",
        isFullTime="y",
        dates=["M", "W", "F"],
        courses={"distinctCourse": 0},
    )

    # Test - faculty_exists should return False
    assert not faculty_model.faculty_exists("distinctName")


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
        dates=["M", "W", "F"],
        courses={"CMSC 161": 5},
    )

    # Add faculty
    result = faculty_model.add_faculty(faculty)

    # Assert
    assert result
    assert faculty_model.faculty_exists("New Test Faculty")


def test_add_faculty_duplicate(faculty_model):
    """
    Test that adding a duplicate faculty fails.

    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Try to add faculty that already exists (Hardy from example.json)
    faculty = build_faculty_config(
        name="Hardy", isFullTime="y", dates=["M", "W", "F"], courses={}
    )

    # Attempt to add
    result = faculty_model.add_faculty(faculty)

    # Assert - should fail (return False)
    assert not result


def test_delete_faculty_success(faculty_model):
    """
    Test successfully deleting a faculty.

    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # First add a test faculty
    faculty = build_faculty_config(
        name="Temp Faculty", isFullTime="y", dates=["M", "W"], courses={}
    )
    faculty_model.add_faculty(faculty)

    # Delete the faculty
    result = faculty_model.delete_faculty("Temp Faculty")

    # Assert
    assert result
    assert not faculty_model.faculty_exists("Temp Faculty")


def test_delete_faculty_not_found(faculty_model):
    """
    Test deleting a non-existent faculty fails.

    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Try to delete non-existent faculty
    result = faculty_model.delete_faculty("NonExistent Faculty")

    # Assert - should fail
    assert not result


def test_modify_faculty_success(faculty_model):
    """
    Test successfully modifying a faculty's field.

    Parameters:
        faculty_model (FacultyModel): Faculty model fixture with test config
    """
    # Add test faculty
    faculty = build_faculty_config(
        name="Modifiable Faculty", isFullTime="y", dates=["M", "W", "F"], courses={}
    )
    faculty_model.add_faculty(faculty)

    # Modify maximum_credits
    result = faculty_model.modify_faculty("Modifiable Faculty", "maximum_credits", 15)

    # Assert
    assert result

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


# ================================================================
# TESTS: validate_faculty_references
# ================================================================


def test_validate_faculty_references(faculty_model):
    """
    Test validating and removing invalid faculty references from courses.
    """
    from scheduler import CourseConfig

    # Add a mock course with one valid and one invalid faculty reference
    test_course = CourseConfig(
        course_id="TEST_REF_101",
        credits=3,
        faculty=["Valid Faculty", "Invalid Faculty Name"],
        room=[],
        lab=[],
        conflicts=[],
    )
    faculty_model.config_model.config.config.courses.append(test_course)

    # Add the valid faculty to the model so it gets recognized
    valid_fac = build_faculty_config(
        name="Valid Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(valid_fac)

    # Run validation
    removed_count = faculty_model.validate_faculty_references()

    # The invalid faculty should have been removed
    assert removed_count >= 1
    assert "Invalid Faculty Name" not in test_course.faculty
    assert "Valid Faculty" in test_course.faculty


def test_validate_faculty_references_all_valid(faculty_model):
    """
    Test validation when all references are valid.
    """
    from scheduler import CourseConfig

    test_course = CourseConfig(
        course_id="TEST_REF_102",
        credits=3,
        faculty=["Valid Only"],
        room=[],
        lab=[],
        conflicts=[],
    )

    # Clear courses to ensure we only test what we add and no other invalid refs exist in example.json
    courses = faculty_model.config_model.config.config.courses
    courses.clear()
    courses.append(test_course)

    valid_fac = build_faculty_config(
        name="Valid Only", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(valid_fac)

    removed_count = faculty_model.validate_faculty_references()

    assert removed_count == 0
    assert "Valid Only" in test_course.faculty


# ================================================================
# TESTS: delete_faculty removes faculty references from courses
# ================================================================


def test_delete_faculty_removes_course_references(faculty_model):
    """
    Test that deleting a faculty also removes their name from any courses
    that reference them (covers the inner branch at line 79).
    """
    from scheduler import CourseConfig

    # Add a faculty to delete
    faculty = build_faculty_config(
        name="ToDelete Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    # Add a course that references this faculty
    test_course = CourseConfig(
        course_id="TEST_DEL_101",
        credits=3,
        faculty=["ToDelete Faculty"],
        room=[],
        lab=[],
        conflicts=[],
    )
    faculty_model.config_model.config.config.courses.append(test_course)

    # Delete the faculty
    result = faculty_model.delete_faculty("ToDelete Faculty")

    assert result
    assert not faculty_model.faculty_exists("ToDelete Faculty")
    assert "ToDelete Faculty" not in test_course.faculty


# ================================================================
# TESTS: get_faculty_by_name returns None for missing faculty
# ================================================================


def test_get_faculty_by_name_not_found(faculty_model):
    """
    Test that get_faculty_by_name returns None when faculty does not exist
    (covers the return None at line 143).
    """
    result = faculty_model.get_faculty_by_name("Nonexistent Person")
    assert result is None


# ================================================================
# TESTS: set_position_type
# ================================================================


def test_set_position_type_fulltime(faculty_model):
    """
    Test setting a faculty to full-time updates credits and course limit.
    """
    faculty = build_faculty_config(
        name="Position Faculty", isFullTime="n", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_position_type("Position Faculty", is_fulltime=True)

    updated = faculty_model.get_faculty_by_name("Position Faculty")
    assert result
    assert updated.maximum_credits == FULL_TIME_MAX_CREDITS
    assert updated.unique_course_limit == FULL_TIME_UNIQUE_COURSE_LIMIT


def test_set_position_type_adjunct(faculty_model):
    """
    Test setting a faculty to adjunct updates credits and course limit.
    """
    faculty = build_faculty_config(
        name="Adjunct Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_position_type("Adjunct Faculty", is_fulltime=False)

    updated = faculty_model.get_faculty_by_name("Adjunct Faculty")
    assert result
    assert updated.maximum_credits == ADJUNCT_MAX_CREDITS
    assert updated.unique_course_limit == ADJUNCT_UNIQUE_COURSE_LIMIT


def test_set_position_type_adjunct_clamps_min_credits(faculty_model):
    """
    Test that switching to adjunct clamps minimum_credits when it exceeds ADJUNCT_MAX_CREDITS.
    """
    faculty = build_faculty_config(
        name="AdjClamp Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)
    faculty_model.modify_faculty("AdjClamp Faculty", "minimum_credits", 10)

    result = faculty_model.set_position_type("AdjClamp Faculty", is_fulltime=False)

    updated = faculty_model.get_faculty_by_name("AdjClamp Faculty")
    assert result
    assert updated.minimum_credits <= ADJUNCT_MAX_CREDITS


def test_set_position_type_not_found(faculty_model):
    """
    Test set_position_type returns False when faculty does not exist.
    """
    result = faculty_model.set_position_type("Ghost Faculty", is_fulltime=True)
    assert not result


# ================================================================
# TESTS: set_maximum_credits
# ================================================================


def test_set_maximum_credits_success(faculty_model):
    """
    Test setting maximum credits updates the faculty.
    """
    faculty = build_faculty_config(
        name="MaxCred Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_maximum_credits("MaxCred Faculty", 10)

    updated = faculty_model.get_faculty_by_name("MaxCred Faculty")
    assert result
    assert updated.maximum_credits == 10


def test_set_maximum_credits_clamps_minimum(faculty_model):
    """
    Test that lowering max below current minimum clamps minimum_credits.
    """
    faculty = build_faculty_config(
        name="ClampMin Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)
    faculty_model.modify_faculty("ClampMin Faculty", "minimum_credits", 8)

    result = faculty_model.set_maximum_credits("ClampMin Faculty", 5)

    updated = faculty_model.get_faculty_by_name("ClampMin Faculty")
    assert result
    assert updated.minimum_credits <= 5


def test_set_maximum_credits_adjunct_limit(faculty_model):
    """
    Test that setting max <= ADJUNCT_MAX_CREDITS sets adjunct course limit.
    """
    faculty = build_faculty_config(
        name="AdjMax Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_maximum_credits("AdjMax Faculty", ADJUNCT_MAX_CREDITS)

    updated = faculty_model.get_faculty_by_name("AdjMax Faculty")
    assert result
    assert updated.unique_course_limit == ADJUNCT_UNIQUE_COURSE_LIMIT


def test_set_maximum_credits_fulltime_limit(faculty_model):
    """
    Test that setting max above ADJUNCT_MAX_CREDITS upgrades course limit to full-time
    when it was previously at the adjunct limit.
    """
    faculty = build_faculty_config(
        name="FTMax Faculty", isFullTime="n", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_maximum_credits("FTMax Faculty", 10)

    updated = faculty_model.get_faculty_by_name("FTMax Faculty")
    assert result
    assert updated.unique_course_limit == FULL_TIME_UNIQUE_COURSE_LIMIT


def test_set_maximum_credits_not_found(faculty_model):
    """
    Test set_maximum_credits returns False when faculty does not exist.
    """
    result = faculty_model.set_maximum_credits("Ghost Faculty", 10)
    assert not result


# ================================================================
# TESTS: build_faculty_config branches
# ================================================================


def test_build_faculty_config_adjunct(faculty_model):
    """
    Test build_faculty_config sets adjunct defaults when is_full_time is False
    (covers lines 235-236).
    """
    data = {
        "name": "Adjunct Builder",
        "is_full_time": False,
        "times": {
            "Monday": [{"start": "09:00", "end": "12:00"}],
        },
        "course_preferences": {},
        "lab_preferences": {},
    }
    result = faculty_model.build_faculty_config(data)

    assert result.maximum_credits == ADJUNCT_MAX_CREDITS
    assert result.unique_course_limit == ADJUNCT_UNIQUE_COURSE_LIMIT


def test_build_faculty_config_days_branch(faculty_model):
    """
    Test build_faculty_config using the 'days' key (else branch, lines 253-260).
    """
    data = {
        "name": "Days Builder",
        "is_full_time": True,
        "days": ["M", "W", "F"],
        "course_preferences": {},
        "lab_preferences": {},
    }
    result = faculty_model.build_faculty_config(data)

    assert "MON" in result.times
    assert "WED" in result.times
    assert "FRI" in result.times
    assert result.times["MON"][0].start == "08:00"
    assert result.times["MON"][0].end == "20:00"
