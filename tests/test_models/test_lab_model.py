# tests/test_models/test_lab_model.py
"""
Unit tests for LabModel using MVC architecture.

Tests cover:
- LabModel CRUD operations (add, delete, modify)
- Lab existence checking
- Lab reference cleanup in courses and faculty
"""

import pytest
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.lab_model import LabModel
from scheduler import CourseConfig, FacultyConfig, TimeRange

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


@pytest.fixture
def lab_model(test_config):
    """
    Create a LabModel with test configuration.
    
    Parameters:
        test_config (str): Path to test config (from test_config fixture)
    
    Returns:
        LabModel: Initialized lab model
    """
    config_model = ConfigModel(test_config)
    return LabModel(config_model)


# ================================================================
# TESTS: Add Lab
# ================================================================

def test_add_lab_success(lab_model):
    """
    Test successfully adding a new lab.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    result = lab_model.add_lab("Python Lab")
    
    assert result == True
    assert lab_model.lab_exists("Python Lab") == True


def test_add_lab_duplicate(lab_model):
    """
    Test that adding a duplicate lab fails.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add first lab
    lab_model.add_lab("Data Structures Lab")
    
    # Try to add duplicate
    result = lab_model.add_lab("Data Structures Lab")
    
    assert result == False


def test_add_lab_with_spaces(lab_model):
    """
    Test adding a lab with spaces in the name.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    result = lab_model.add_lab("Advanced Algorithms Lab")
    
    assert result == True
    assert lab_model.lab_exists("Advanced Algorithms Lab") == True


def test_add_lab_special_characters(lab_model):
    """
    Test adding a lab with special characters.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    result = lab_model.add_lab("Lab-C++ (Intro)")
    
    assert result == True
    assert lab_model.lab_exists("Lab-C++ (Intro)") == True


def test_add_lab_numeric_name(lab_model):
    """
    Test adding a lab with a numeric name.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    result = lab_model.add_lab("CS101")
    
    assert result == True
    assert lab_model.lab_exists("CS101") == True


def test_add_lab_long_name(lab_model):
    """
    Test adding a lab with a long name.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    long_name = "Advanced Object-Oriented Programming and Design Patterns Laboratory"
    result = lab_model.add_lab(long_name)
    
    assert result == True
    assert lab_model.lab_exists(long_name) == True


def test_add_existing_lab_from_config(lab_model):
    """
    Test that adding a lab that already exists in example.json fails.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Linux exists in example.json
    result = lab_model.add_lab("Linux")
    
    assert result == False


# ================================================================
# TESTS: Delete Lab
# ================================================================

def test_delete_lab_success(lab_model):
    """
    Test successfully deleting a lab.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add test lab
    lab_model.add_lab("Delete Me Lab")
    
    # Delete it
    result = lab_model.delete_lab("Delete Me Lab")
    
    assert result == True
    assert lab_model.lab_exists("Delete Me Lab") == False


def test_delete_lab_not_found(lab_model):
    """
    Test deleting a non-existent lab fails.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    result = lab_model.delete_lab("NonExistent Lab")
    
    assert result == False


def test_delete_lab_removes_from_courses(lab_model):
    """
    Test that deleting a lab removes it from courses.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add lab and course that uses it
    lab_model.add_lab("TestLab 101")
    
    config_model = lab_model.config_model
    course = CourseConfig(
        course_id="LABTEST 101",
        credits=3,
        room=[],
        lab=["TestLab 101"],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course)
    config_model.safe_save()
    config_model.reload()
    
    # Delete lab
    lab_model.delete_lab("TestLab 101")
    
    # Verify lab removed from course
    updated_course = [c for c in config_model.config.config.courses if c.course_id == "LABTEST 101"][0]
    assert "TestLab 101" not in updated_course.lab


def test_delete_lab_removes_from_faculty_preferences(lab_model):
    """
    Test that deleting a lab removes it from faculty preferences.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add lab and faculty with preference
    lab_model.add_lab("PrefLab 101")
    
    config_model = lab_model.config_model
    faculty = FacultyConfig(
        name="Test Lab Faculty",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={},
        lab_preferences={"PrefLab 101": 7},
        maximum_days=5,
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    config_model.config.config.faculty.append(faculty)
    config_model.safe_save()
    config_model.reload()
    
    # Delete lab
    lab_model.delete_lab("PrefLab 101")
    
    # Verify lab removed from faculty preferences
    updated_faculty = [f for f in config_model.config.config.faculty if f.name == "Test Lab Faculty"][0]
    assert "PrefLab 101" not in updated_faculty.lab_preferences


# ================================================================
# TESTS: Modify Lab
# ================================================================

def test_modify_lab_success(lab_model):
    """
    Test successfully modifying a lab name.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add test lab
    lab_model.add_lab("OldLab 101")
    
    # Modify it
    result = lab_model.modify_lab("OldLab 101", "NewLab 101")
    
    assert result == True
    assert lab_model.lab_exists("OldLab 101") == False
    assert lab_model.lab_exists("NewLab 101") == True


def test_modify_lab_not_found(lab_model):
    """
    Test modifying a non-existent lab fails.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    result = lab_model.modify_lab("NonExistent", "NewName")
    
    assert result == False


def test_modify_lab_new_name_exists(lab_model):
    """
    Test modifying to an existing lab name fails.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add two labs
    lab_model.add_lab("Lab A")
    lab_model.add_lab("Lab B")
    
    # Try to rename Lab A to Lab B (which already exists)
    result = lab_model.modify_lab("Lab A", "Lab B")
    
    assert result == False


def test_modify_lab_updates_courses(lab_model):
    """
    Test that modifying a lab updates course references.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add lab and course
    lab_model.add_lab("OldCourseLab")
    
    config_model = lab_model.config_model
    course = CourseConfig(
        course_id="LABUPDATE 101",
        credits=3,
        room=[],
        lab=["OldCourseLab"],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course)
    config_model.safe_save()
    config_model.reload()
    
    # Modify lab
    lab_model.modify_lab("OldCourseLab", "NewCourseLab")
    
    # Verify course updated
    updated_course = [c for c in config_model.config.config.courses if c.course_id == "LABUPDATE 101"][0]
    assert "OldCourseLab" not in updated_course.lab
    assert "NewCourseLab" in updated_course.lab


def test_modify_lab_updates_faculty_preferences(lab_model):
    """
    Test that modifying a lab updates faculty preferences.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add lab and faculty
    lab_model.add_lab("OldFacLab")
    
    config_model = lab_model.config_model
    faculty = FacultyConfig(
        name="Update Lab Faculty",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={},
        lab_preferences={"OldFacLab": 9},
        maximum_days=5,
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    config_model.config.config.faculty.append(faculty)
    config_model.safe_save()
    config_model.reload()
    
    # Modify lab
    lab_model.modify_lab("OldFacLab", "NewFacLab")
    
    # Verify faculty updated
    updated_faculty = [f for f in config_model.config.config.faculty if f.name == "Update Lab Faculty"][0]
    assert "OldFacLab" not in updated_faculty.lab_preferences
    assert "NewFacLab" in updated_faculty.lab_preferences
    assert updated_faculty.lab_preferences["NewFacLab"] == 9  # Weight preserved


def test_modify_lab_multiple_courses(lab_model):
    """
    Test modifying a lab updates all courses that use it.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add lab and multiple courses
    lab_model.add_lab("SharedLab")
    
    config_model = lab_model.config_model
    course1 = CourseConfig(
        course_id="MULTI1",
        credits=3,
        room=[],
        lab=["SharedLab"],
        faculty=[],
        conflicts=[]
    )
    course2 = CourseConfig(
        course_id="MULTI2",
        credits=4,
        room=[],
        lab=["SharedLab"],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course1)
    config_model.config.config.courses.append(course2)
    config_model.safe_save()
    config_model.reload()
    
    # Modify lab
    lab_model.modify_lab("SharedLab", "RenamedLab")
    
    # Verify both courses updated
    updated_course1 = [c for c in config_model.config.config.courses if c.course_id == "MULTI1"][0]
    updated_course2 = [c for c in config_model.config.config.courses if c.course_id == "MULTI2"][0]
    
    assert "RenamedLab" in updated_course1.lab
    assert "RenamedLab" in updated_course2.lab


# ================================================================
# TESTS: Lab Existence and Retrieval
# ================================================================

def test_lab_exists_true(lab_model):
    """
    Test lab_exists returns True for existing lab.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    lab_model.add_lab("Exists Lab")
    
    assert lab_model.lab_exists("Exists Lab") == True


def test_lab_exists_false(lab_model):
    """
    Test lab_exists returns False for non-existent lab.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    assert lab_model.lab_exists("NonExistent Lab") == False


def test_get_all_labs(lab_model):
    """
    Test retrieving all labs.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    all_labs = lab_model.get_all_labs()
    
    assert isinstance(all_labs, list)
    assert len(all_labs) > 0  # example.json should have labs


def test_get_affected_courses(lab_model):
    # Add labs first
    lab_model.add_lab("Affected Lab")
    lab_model.add_lab("Other Lab")  # ADD THIS LINE
    
    config_model = lab_model.config_model
    course1 = CourseConfig(
        course_id="LABCOURSE1",
        credits=3,
        room=[],
        lab=["Affected Lab"],
        faculty=[],
        conflicts=[]
    )
    course2 = CourseConfig(
        course_id="LABCOURSE2",
        credits=3,
        room=[],
        lab=["Other Lab"],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course1)
    config_model.config.config.courses.append(course2)
    config_model.safe_save()
    config_model.reload()
    
    # Get affected courses
    affected = lab_model.get_affected_courses("Affected Lab")
    
    assert len(affected) == 1
    assert affected[0].course_id == "LABCOURSE1"


def test_get_affected_faculty(lab_model):
    """
    Test getting faculty affected by a lab.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add lab and faculty
    lab_model.add_lab("Pref Lab")
    
    config_model = lab_model.config_model
    faculty1 = FacultyConfig(
        name="Lab Faculty A",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={},
        lab_preferences={"Pref Lab": 6},
        maximum_days=5,
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    faculty2 = FacultyConfig(
        name="Lab Faculty B",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={},
        lab_preferences={},
        maximum_days=5,
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    config_model.config.config.faculty.append(faculty1)
    config_model.config.config.faculty.append(faculty2)
    config_model.safe_save()
    config_model.reload()
    
    # Get affected faculty
    affected = lab_model.get_affected_faculty("Pref Lab")
    
    assert len(affected) == 1
    assert affected[0].name == "Lab Faculty A"


def test_get_affected_courses_no_matches(lab_model):
    """
    Test getting affected courses when none use the lab.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add lab but no courses use it
    lab_model.add_lab("Unused Lab")
    
    affected = lab_model.get_affected_courses("Unused Lab")
    
    assert len(affected) == 0


def test_get_affected_faculty_no_matches(lab_model):
    """
    Test getting affected faculty when none prefer the lab.
    
    Parameters:
        lab_model (LabModel): Lab model fixture
    """
    # Add lab but no faculty prefer it
    lab_model.add_lab("Unpopular Lab")
    
    affected = lab_model.get_affected_faculty("Unpopular Lab")
    
    assert len(affected) == 0