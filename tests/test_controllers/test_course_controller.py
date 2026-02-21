# tests/test_controllers/test_course_controller.py
"""
Unit tests for CourseController using MVC architecture.

Tests cover:
- CourseController workflow orchestration
- View interaction (mocked)
- Model coordination
- Course modification and deletion workflows
"""

import pytest
from unittest.mock import Mock
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.course_model import CourseModel
from models.conflict_model import ConflictModel
from controllers.course_controller import CourseController
from scheduler import CourseConfig

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
def course_controller(config_model):
    """
    Create CourseController with mocked view.
    
    Returns:
        tuple: (controller, mock_view, course_model)
    """
    course_model = CourseModel(config_model)
    mock_view = Mock()
    controller = CourseController(course_model, mock_view)
    return controller, mock_view, course_model


@pytest.fixture
def conflict_model(config_model):
    """Create ConflictModel for test verification."""
    return ConflictModel(config_model)


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def build_test_course(course_id="TEST 101", credits=3, rooms=None, labs=None):
    """Build a test course."""
    return CourseConfig(
        course_id=course_id,
        credits=credits,
        room=rooms if rooms is not None else [],
        lab=labs if labs is not None else [],
        faculty=[],
        conflicts=[]
    )


# ================================================================
# TESTS: Modify Course - Single Field
# ================================================================

def test_modify_credits(course_controller):
    """
    Test modifying course credits.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3, rooms=["SCI 100"])
    model.add_course(course)
    
    # Mock user modifying credits
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.return_value = 1  # Credits
    mock_view.get_integer_input.return_value = 4
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify
    updated = model.get_course_by_id("CMSC 140")
    assert updated.credits == 4
    assert updated.room == ["SCI 100"]  # Unchanged


def test_modify_room(course_controller):
    """
    Test modifying course room.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3, rooms=["SCI 100"])
    model.add_course(course)
    
    # Mock user modifying room
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.return_value = 2  # Room
    mock_view.get_room_list.return_value = ["SCI 200"]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify
    updated = model.get_course_by_id("CMSC 140")
    assert updated.credits == 3  # Unchanged
    assert "SCI 200" in updated.room


def test_modify_lab(course_controller):
    """
    Test modifying course lab.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3, rooms=["SCI 100"])
    model.add_course(course)
    
    # Mock user modifying lab
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.return_value = 3  # Lab
    mock_view.get_lab_list.return_value = ["LAB 1"]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify
    updated = model.get_course_by_id("CMSC 140")
    assert updated.credits == 3  # Unchanged
    assert updated.room == ["SCI 100"]  # Unchanged
    assert "LAB 1" in updated.lab


# ================================================================
# TESTS: Modify Course - Multiple Fields
# ================================================================

def test_modify_multiple_fields(course_controller):
    """
    Test modifying multiple course fields.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3, rooms=["SCI 100"])
    model.add_course(course)
    
    # Mock user modifying credits and room
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.side_effect = [
        1,  # Credits
        2,  # Room
        10  # Exit
    ]
    mock_view.get_integer_input.return_value = 4
    mock_view.get_room_list.return_value = ["SCI 200"]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify
    updated = model.get_course_by_id("CMSC 140")
    assert updated.credits == 4
    assert "SCI 200" in updated.room


def test_modify_all_fields(course_controller):
    """
    Test modifying all course fields.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3, rooms=["SCI 100"])
    model.add_course(course)
    
    # Mock user modifying all fields
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.side_effect = [
        1,  # Credits
        2,  # Room
        3,  # Lab
        10  # Exit
    ]
    mock_view.get_integer_input.return_value = 4
    mock_view.get_room_list.return_value = ["SCI 200"]
    mock_view.get_lab_list.return_value = ["LAB 1"]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify
    updated = model.get_course_by_id("CMSC 140")
    assert updated.credits == 4
    assert "SCI 200" in updated.room
    assert "LAB 1" in updated.lab


def test_modify_nothing(course_controller):
    """
    Test selecting course but making no modifications.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3, rooms=["SCI 100"])
    model.add_course(course)
    
    # Mock user exiting without changes
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.return_value = 10  # Exit immediately
    
    # Execute
    controller.modify_course()
    
    # Verify no changes
    updated = model.get_course_by_id("CMSC 140")
    assert updated.credits == 3
    assert updated.room == ["SCI 100"]
    assert updated.lab == []


# ================================================================
# TESTS: Modify Course - Edge Cases
# ================================================================

def test_modify_credits_zero(course_controller):
    """
    Test setting credits to zero (should fail validation).
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3)
    model.add_course(course)
    
    # Mock user trying to set credits to 0
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.return_value = 1  # Credits
    mock_view.get_integer_input.return_value = 0
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify rejected (credits unchanged)
    updated = model.get_course_by_id("CMSC 140")
    assert updated.credits == 3


def test_modify_room_empty(course_controller):
    """
    Test setting room to empty.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3, rooms=["SCI 100"])
    model.add_course(course)
    
    # Mock user clearing room
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.return_value = 2  # Room
    mock_view.get_room_list.return_value = []  # Empty
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify
    updated = model.get_course_by_id("CMSC 140")
    assert updated.room == []


def test_modify_credits_negative(course_controller):
    """
    Test that negative credits are rejected.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3)
    model.add_course(course)
    
    # Mock user trying negative credits
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.return_value = 1
    mock_view.get_integer_input.return_value = -5
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify rejected
    updated = model.get_course_by_id("CMSC 140")
    assert updated.credits == 3


def test_course_id_unchanged(course_controller):
    """
    Test that course ID never changes.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 140", credits=3, rooms=["SCI 100"])
    model.add_course(course)
    
    # Mock modifications
    mock_view.select_course_from_list.return_value = ("CMSC 140", 0)
    mock_view.get_modification_choice.side_effect = [1, 10]
    mock_view.get_integer_input.return_value = 4
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_course()
    
    # Verify ID unchanged
    updated = model.get_course_by_id("CMSC 140")
    assert updated.course_id == "CMSC 140"


# ================================================================
# TESTS: Delete Course Workflow
# ================================================================

def test_delete_existing_course(course_controller):
    """
    Test deleting an existing course.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 162")
    model.add_course(course)
    
    # Mock user selecting and confirming deletion
    mock_view.select_course_from_list.return_value = ("CMSC 162.01", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_course()
    
    # Verify deleted
    assert model.course_exists("CMSC 162") == False


def test_delete_course_removes_conflicts(course_controller, conflict_model):
    """
    Test that deleting a course removes it from other courses' conflicts.
    
    Parameters:
        course_controller: Controller fixture
        conflict_model: Conflict model for verification
    """
    controller, mock_view, model = course_controller
    
    # Setup: Two courses with mutual conflict
    course_a = build_test_course("CMSC 140")
    course_b = build_test_course("CMSC 161")
    model.add_course(course_a)
    model.add_course(course_b)
    conflict_model.add_conflict("CMSC 140", "CMSC 161")
    
    # Mock user deleting CMSC 161
    mock_view.select_course_from_list.return_value = ("CMSC 161.01", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_course()
    
    # Verify conflict removed from CMSC 140
    model.config_model.reload()
    course_a_updated = model.get_course_by_id("CMSC 140")
    assert "CMSC 161" not in course_a_updated.conflicts


def test_delete_course_canceled(course_controller):
    """
    Test that canceling deletion preserves course.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup
    course = build_test_course("CMSC 162")
    model.add_course(course)
    
    # Mock user canceling
    mock_view.select_course_from_list.return_value = ("CMSC 162.01", 0)
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.delete_course()
    
    # Verify still exists
    assert model.course_exists("CMSC 162") == True


def test_delete_specific_section(course_controller):
    """
    Test deleting a specific section leaves other sections intact.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup: Two sections of CMSC 161
    course1 = build_test_course("CMSC 161")
    course2 = build_test_course("CMSC 161")
    model.config_model.config.config.courses.append(course1)
    model.config_model.config.config.courses.append(course2)
    model.config_model.safe_save()
    model.config_model.reload()
    
    # Get section index
    courses_with_sections = model.get_courses_with_sections()
    second_section_idx = None
    for label, idx, course in courses_with_sections:
        if course.course_id == "CMSC 161" and ".02" in label:
            second_section_idx = idx
            break
    
    # Mock user deleting section .02
    mock_view.select_course_from_list.return_value = ("CMSC 161.02", second_section_idx)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_course()
    
    # Verify one section remains
    remaining = [c for c in model.get_all_courses() if c.course_id == "CMSC 161"]
    assert len(remaining) == 1


def test_delete_course_not_found(course_controller):
    """
    Test error when trying to delete non-existent course.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Execute with no courses
    controller.delete_course()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


# ================================================================
# TESTS: Add Course Workflow
# ================================================================

def test_add_course_success(course_controller):
    """
    Test successfully adding a new course.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Mock user input
    mock_view.get_course_id.return_value = "TEST 101"
    mock_view.get_integer_input.return_value = 3  # Credits
    mock_view.get_room_list.return_value = ["Roddy 140"]
    mock_view.get_lab_list.return_value = []
    mock_view.get_faculty_list.return_value = []
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_course()
    
    # Verify
    assert model.course_exists("TEST 101") == True
    mock_view.display_message.assert_called()


def test_add_course_duplicate(course_controller):
    """
    Test that adding duplicate course ID fails.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Setup: Add course first
    course = build_test_course("CMSC 140")
    model.add_course(course)
    
    # Mock user trying to add duplicate
    mock_view.get_course_id.return_value = "CMSC 140"
    
    # Execute
    controller.add_course()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


def test_add_course_user_cancels(course_controller):
    """
    Test canceling course addition.
    
    Parameters:
        course_controller: Controller fixture
    """
    controller, mock_view, model = course_controller
    
    # Mock user input then cancel
    mock_view.get_course_id.return_value = "CANCEL 101"
    mock_view.get_integer_input.return_value = 3
    mock_view.get_room_list.return_value = []
    mock_view.get_lab_list.return_value = []
    mock_view.get_faculty_list.return_value = []
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.add_course()
    
    # Verify not added
    assert model.course_exists("CANCEL 101") == False