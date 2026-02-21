# tests/test_controllers/test_lab_controller.py
"""
Unit tests for LabController using MVC architecture.

Tests cover:
- LabController workflow orchestration
- View interaction (mocked)
- Model coordination
- Lab addition and deletion workflows
"""

import pytest
from unittest.mock import Mock
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.lab_model import LabModel
from models.course_model import CourseModel
from controllers.lab_controller import LabController
from scheduler import CourseConfig, FacultyConfig, TimeRange

# Test configuration
TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_copy.json"


# ================================================================
# PYTEST FIXTURES
# ================================================================

@pytest.fixture
def test_config():
    """Create a fresh copy of example.json for each test."""
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def config_model(test_config):
    """Create ConfigModel with test configuration."""
    return ConfigModel(test_config)


@pytest.fixture
def lab_controller(config_model):
    """
    Create LabController with mocked view.
    
    Returns:
        tuple: (controller, mock_view, lab_model)
    """
    lab_model = LabModel(config_model)
    mock_view = Mock()
    controller = LabController(lab_model, mock_view)
    return controller, mock_view, lab_model


# ================================================================
# TESTS: Add Lab Workflow
# ================================================================

def test_add_lab_valid_name(lab_controller):
    """
    Test adding a lab with a valid name.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Mock user input
    mock_view.get_lab_name.return_value = "Python Lab"
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_lab()
    
    # Verify
    assert model.lab_exists("Python Lab") == True
    mock_view.display_message.assert_called()


def test_add_lab_with_spaces(lab_controller):
    """
    Test that lab name with leading/trailing spaces is trimmed.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Mock user input with spaces
    mock_view.get_lab_name.return_value = "  Advanced Algorithms Lab  "
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_lab()
    
    # Verify spaces trimmed
    assert model.lab_exists("Advanced Algorithms Lab") == True


def test_add_lab_special_characters(lab_controller):
    """
    Test adding lab with special characters.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Mock user input
    mock_view.get_lab_name.return_value = "Lab-C++ (Intro)"
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_lab()
    
    # Verify
    assert model.lab_exists("Lab-C++ (Intro)") == True


def test_add_lab_numeric_name(lab_controller):
    """
    Test adding lab with numeric name.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Mock user input
    mock_view.get_lab_name.return_value = "CS101"
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_lab()
    
    # Verify
    assert model.lab_exists("CS101") == True


def test_add_lab_long_name(lab_controller):
    """
    Test adding lab with a long name.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    long_name = "Advanced Object-Oriented Programming and Design Patterns Laboratory"
    
    # Mock user input
    mock_view.get_lab_name.return_value = long_name
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_lab()
    
    # Verify
    assert model.lab_exists(long_name) == True


def test_add_lab_user_cancels(lab_controller):
    """
    Test canceling lab addition.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Mock user input then cancel
    mock_view.get_lab_name.return_value = "Test Lab"
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.add_lab()
    
    # Verify not added
    assert model.lab_exists("Test Lab") == False


def test_add_lab_duplicate(lab_controller):
    """
    Test that adding duplicate lab fails.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup: Add lab first
    model.add_lab("Existing Lab")
    
    # Mock user trying to add duplicate
    mock_view.get_lab_name.return_value = "Existing Lab"
    
    # Execute
    controller.add_lab()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


# ================================================================
# TESTS: Delete Lab Workflow
# ================================================================

def test_delete_existing_lab(lab_controller):
    """
    Test deleting an existing lab.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup
    model.add_lab("Linux")
    
    # Mock user selecting and confirming deletion
    mock_view.select_lab_from_list.return_value = ("Linux", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_lab()
    
    # Verify deleted
    assert model.lab_exists("Linux") == False
    mock_view.display_message.assert_called()


def test_delete_lab_removes_from_courses(lab_controller):
    """
    Test that deleting a lab removes it from all courses.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup: Add lab and courses using it
    model.add_lab("Linux")
    
    config_model = model.config_model
    course1 = CourseConfig(
        course_id="CMSC 161",
        credits=3,
        room=[],
        lab=["Linux"],
        faculty=[],
        conflicts=[]
    )
    course2 = CourseConfig(
        course_id="CMSC 162",
        credits=3,
        room=[],
        lab=["Linux"],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course1)
    config_model.config.config.courses.append(course2)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user deleting lab
    mock_view.select_lab_from_list.return_value = ("Linux", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_lab()
    
    # Verify lab removed from courses
    config_model.reload()
    cmsc161 = next((c for c in config_model.config.config.courses if c.course_id == "CMSC 161"), None)
    cmsc162 = next((c for c in config_model.config.config.courses if c.course_id == "CMSC 162"), None)
    
    if cmsc161:
        assert "Linux" not in cmsc161.lab
    if cmsc162:
        assert "Linux" not in cmsc162.lab


def test_delete_lab_removes_from_faculty_preferences(lab_controller):
    """
    Test that deleting a lab removes it from faculty preferences.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup: Add lab and faculty with preference
    model.add_lab("Mac")
    
    config_model = model.config_model
    faculty1 = FacultyConfig(
        name="Zoppetti",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={},
        lab_preferences={"Mac": 5},
        maximum_days=5,
        mandatory_days=[],
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    faculty2 = FacultyConfig(
        name="Brooks",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={},
        lab_preferences={"Mac": 3},
        maximum_days=5,
        mandatory_days=[],
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    config_model.config.config.faculty.append(faculty1)
    config_model.config.config.faculty.append(faculty2)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user deleting lab
    mock_view.select_lab_from_list.return_value = ("Mac", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_lab()
    
    # Verify lab removed from faculty preferences
    config_model.reload()
    zoppetti = next((f for f in config_model.config.config.faculty if f.name == "Zoppetti"), None)
    brooks = next((f for f in config_model.config.config.faculty if f.name == "Brooks"), None)
    
    if zoppetti:
        assert "Mac" not in zoppetti.lab_preferences
    if brooks:
        assert "Mac" not in brooks.lab_preferences


def test_delete_lab_preserves_other_labs(lab_controller):
    """
    Test that deleting one lab doesn't affect other labs.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup: Add multiple labs
    model.add_lab("Linux")
    model.add_lab("Mac")
    model.add_lab("Windows")
    
    # Mock user deleting one lab
    mock_view.select_lab_from_list.return_value = ("Windows", 2)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_lab()
    
    # Verify other labs preserved
    assert model.lab_exists("Linux") == True
    assert model.lab_exists("Mac") == True
    assert model.lab_exists("Windows") == False


def test_delete_lab_user_cancels(lab_controller):
    """
    Test canceling lab deletion.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup
    model.add_lab("Mac")
    
    # Mock user canceling
    mock_view.select_lab_from_list.return_value = ("Mac", 0)
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.delete_lab()
    
    # Verify lab still exists
    assert model.lab_exists("Mac") == True


def test_delete_lab_only_removes_specified_lab(lab_controller):
    """
    Test that only the specified lab is removed from courses.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup: Course with multiple labs
    model.add_lab("Linux")
    model.add_lab("Mac")
    
    config_model = model.config_model
    course = CourseConfig(
        course_id="CMSC 162",
        credits=3,
        room=[],
        lab=["Linux", "Mac"],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user deleting Linux
    mock_view.select_lab_from_list.return_value = ("Linux", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_lab()
    
    # Verify Linux removed but Mac remains
    config_model.reload()
    cmsc162 = next((c for c in config_model.config.config.courses if c.course_id == "CMSC 162"), None)
    
    if cmsc162:
        assert "Linux" not in cmsc162.lab
        assert "Mac" in cmsc162.lab


def test_delete_lab_courses_without_lab_unchanged(lab_controller):
    """
    Test that courses without the deleted lab remain unchanged.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup: Add lab and course without it
    model.add_lab("Linux")
    
    config_model = model.config_model
    course = CourseConfig(
        course_id="CMSC 140",
        credits=3,
        room=[],
        lab=[],  # No labs
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user deleting lab
    mock_view.select_lab_from_list.return_value = ("Linux", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_lab()
    
    # Verify course unchanged
    config_model.reload()
    cmsc140 = next((c for c in config_model.config.config.courses if c.course_id == "CMSC 140"), None)
    
    if cmsc140:
        assert len(cmsc140.lab) == 0


def test_delete_lab_faculty_preferences_preserved(lab_controller):
    """
    Test that other faculty lab preferences are preserved.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Setup: Faculty with multiple lab preferences
    model.add_lab("Linux")
    model.add_lab("Mac")
    model.add_lab("Windows")
    
    config_model = model.config_model
    faculty = FacultyConfig(
        name="Zoppetti",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={},
        lab_preferences={"Linux": 5, "Mac": 3, "Windows": 7},
        maximum_days=5,
        mandatory_days=[],
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    config_model.config.config.faculty.append(faculty)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user deleting Mac
    mock_view.select_lab_from_list.return_value = ("Mac", 1)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_lab()
    
    # Verify other preferences preserved
    config_model.reload()
    zoppetti = next((f for f in config_model.config.config.faculty if f.name == "Zoppetti"), None)
    
    if zoppetti:
        assert zoppetti.lab_preferences.get("Linux") == 5
        assert zoppetti.lab_preferences.get("Windows") == 7
        assert "Mac" not in zoppetti.lab_preferences


def test_delete_lab_no_labs_exist(lab_controller):
    """
    Test error when trying to delete with no labs.
    
    Parameters:
        lab_controller: Controller fixture
    """
    controller, mock_view, model = lab_controller
    
    # Execute with no labs
    controller.delete_lab()
    
    # Verify error displayed
    mock_view.display_error.assert_called()