# tests/test_models/test_course_model.py
"""
Unit tests for CourseModel using MVC architecture.

Tests cover:
- CourseModel CRUD operations (add, delete, modify)
- Course existence checking
- Course retrieval methods
- Section handling
"""

import pytest
import shutil
from pathlib import Path
from scheduler import CourseConfig

from models.config_model import ConfigModel
from models.course_model import CourseModel

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
def course_model(test_config):
    """
    Create a CourseModel with test configuration.
    
    Parameters:
        test_config (str): Path to test config (from test_config fixture)
    
    Returns:
        CourseModel: Initialized course model
    """
    config_model = ConfigModel(test_config)
    return CourseModel(config_model)


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def build_test_course(course_id="TEST 101", credits=3, rooms=None, labs=None, 
                      faculty=None, conflicts=None) -> CourseConfig:
    """
    Build a test CourseConfig object.
    
    Parameters:
        course_id (str): Course ID
        credits (int): Number of credits
        rooms (list): List of room names
        labs (list): List of lab names
        faculty (list): List of faculty names
        conflicts (list): List of conflicting course IDs
    
    Returns:
        CourseConfig: Configured course object
    """
    return CourseConfig(
        course_id=course_id,
        credits=credits,
        room=rooms if rooms is not None else [],
        lab=labs if labs is not None else [],
        faculty=faculty if faculty is not None else [],
        conflicts=conflicts if conflicts is not None else []
    )


# ================================================================
# TESTS: Course CRUD Operations
# ================================================================

def test_add_course_success(course_model):
    """
    Test successfully adding a new course.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    course = build_test_course(
        course_id="TEST 101",
        credits=3,
        rooms=["Roddy 140"],
        labs=["Linux"],
        faculty=["Hardy"],
        conflicts=[]
    )
    
    result = course_model.add_course(course)
    
    assert result == True
    assert course_model.course_exists("TEST 101") == True


def test_add_course_duplicate(course_model):
    """
    Test that adding a duplicate course fails.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    # Add first course
    course = build_test_course(course_id="DUP 101")
    course_model.add_course(course)
    
    # Try to add duplicate
    duplicate = build_test_course(course_id="DUP 101")
    result = course_model.add_course(duplicate)
    
    assert result == False


def test_add_course_empty_rooms_labs(course_model):
    """
    Test adding a course with empty rooms and labs lists.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    course = build_test_course(
        course_id="EMPTY 101",
        rooms=[],
        labs=[],
        faculty=["Hardy"]
    )
    
    result = course_model.add_course(course)
    
    assert result == True
    assert course_model.course_exists("EMPTY 101") == True


def test_delete_course_success(course_model):
    """
    Test successfully deleting a course.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    # Add test course
    course = build_test_course(course_id="DELETE 101")
    course_model.add_course(course)
    
    # Delete it
    result = course_model.delete_course("DELETE 101")
    
    assert result == True
    assert course_model.course_exists("DELETE 101") == False


def test_delete_course_not_found(course_model):
    """
    Test deleting a non-existent course fails.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    result = course_model.delete_course("NONEXISTENT 999")
    
    assert result == False


def test_delete_course_removes_conflicts(course_model):
    """
    Test that deleting a course removes it from other courses' conflict lists.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    # Add two courses with mutual conflicts
    course_a = build_test_course(course_id="CONF A", conflicts=["CONF B"])
    course_b = build_test_course(course_id="CONF B", conflicts=["CONF A"])
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    
    # Delete course A
    course_model.delete_course("CONF A")
    
    # Verify CONF B no longer has CONF A in conflicts
    course_b_updated = course_model.get_course_by_id("CONF B")
    assert "CONF A" not in course_b_updated.conflicts


def test_modify_course_success(course_model):
    """
    Test successfully modifying a course.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    # Add test course
    course = build_test_course(course_id="MODIFY 101", credits=3)
    course_model.add_course(course)
    
    # Modify credits
    result = course_model.modify_course("MODIFY 101", credits=4)
    
    assert result == True
    
    # Verify change
    modified = course_model.get_course_by_id("MODIFY 101")
    assert modified.credits == 4


def test_modify_course_not_found(course_model):
    """
    Test modifying a non-existent course fails.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    result = course_model.modify_course("NONEXISTENT 999", credits=4)
    
    assert result == False


def test_modify_course_negative_credits(course_model):
    """
    Test that modifying to negative credits fails.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    # Add test course
    course = build_test_course(course_id="NEG 101", credits=3)
    course_model.add_course(course)
    
    # Try to set negative credits
    result = course_model.modify_course("NEG 101", credits=-1)
    
    assert result == False


def test_modify_course_multiple_fields(course_model):
    # Add test course
    course = build_test_course(
        course_id="MULTI 101",
        credits=3,
        rooms=["Roddy 140"],
        faculty=["Hardy"]  # Hardy exists in example.json
    )
    course_model.add_course(course)
    
    # Modify multiple fields - use Hardy again instead of Smith
    result = course_model.modify_course(
        "MULTI 101",
        credits=4,
        room=["Roddy 136", "Roddy 140"],
        faculty=["Hardy"]  # Changed from ["Hardy", "Smith"]
    )
    
    assert result == True
    
    # Verify all changes
    modified = course_model.get_course_by_id("MULTI 101")
    assert modified.credits == 4
    assert "Roddy 136" in modified.room
    assert "Hardy" in modified.faculty

# ================================================================
# TESTS: Course Existence and Retrieval
# ================================================================

def test_course_exists_true(course_model):
    """
    Test course_exists returns True for existing course.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    course = build_test_course(course_id="EXISTS 101")
    course_model.add_course(course)
    
    assert course_model.course_exists("EXISTS 101") == True


def test_course_exists_false(course_model):
    """
    Test course_exists returns False for non-existent course.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    assert course_model.course_exists("NONEXISTENT 999") == False


def test_get_course_by_id_found(course_model):
    """
    Test retrieving an existing course by ID.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    course = build_test_course(course_id="GET 101", credits=4)
    course_model.add_course(course)
    
    retrieved = course_model.get_course_by_id("GET 101")
    
    assert retrieved is not None
    assert retrieved.course_id == "GET 101"
    assert retrieved.credits == 4


def test_get_course_by_id_not_found(course_model):
    """
    Test retrieving a non-existent course returns None.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    retrieved = course_model.get_course_by_id("NONEXISTENT 999")
    
    assert retrieved is None


def test_get_all_courses(course_model):
    """
    Test retrieving all courses.
    
    Parameters:
        course_model (CourseModel): Course model fixture
    """
    all_courses = course_model.get_all_courses()
    
    assert isinstance(all_courses, list)
    assert len(all_courses) > 0  # example.json should have courses


# ================================================================
# TESTS: Section Handling
# ================================================================

def test_get_courses_with_sections(course_model):
    # Add multiple sections by directly appending (bypass duplicate check)
    course1 = build_test_course(course_id="SECT 101")
    course2 = build_test_course(course_id="SECT 101")
    
    # Directly append to bypass duplicate prevention
    course_model.config_model.config.config.courses.append(course1)
    course_model.config_model.config.config.courses.append(course2)
    course_model.config_model.safe_save()
    course_model.config_model.reload()
    
    courses_with_sections = course_model.get_courses_with_sections()
    
    # Find sections for SECT 101
    sect_101_sections = [
        (label, idx, course) for label, idx, course in courses_with_sections
        if course.course_id == "SECT 101"
    ]
    
    # Should have 2 sections
    assert len(sect_101_sections) == 2

def test_delete_course_by_section_index(course_model):
    # Add two sections by directly appending
    course1 = build_test_course(course_id="DELSECT 101")
    course2 = build_test_course(course_id="DELSECT 101")
    
    # Directly append
    course_model.config_model.config.config.courses.append(course1)
    course_model.config_model.config.config.courses.append(course2)
    course_model.config_model.safe_save()
    course_model.config_model.reload()
        
    # Get courses with sections
    courses_with_sections = course_model.get_courses_with_sections()
    
    # Find first DELSECT 101 section
    for label, idx, course in courses_with_sections:
        if course.course_id == "DELSECT 101":
            first_index = idx
            break
    
    # Delete just that section
    result = course_model.delete_course("DELSECT 101", section_index=first_index)
    
    assert result == True
    # At least one section should still exist
    assert course_model.course_exists("DELSECT 101") == True