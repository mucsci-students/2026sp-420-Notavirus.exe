# tests/test_controllers/test_conflict_controller.py
"""
Unit tests for ConflictController using MVC architecture.

Tests cover:
- ConflictController workflow orchestration
- View interaction (mocked)
- Model coordination
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.conflict_model import ConflictModel
from models.course_model import CourseModel
from controllers.conflict_controller import ConflictController
from scheduler import CourseConfig

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
def config_model(test_config):
    """Create ConfigModel with test configuration."""
    return ConfigModel(test_config)


@pytest.fixture
def conflict_controller(config_model):
    """
    Create ConflictController with mocked view.
    
    Parameters:
        config_model (ConfigModel): Config model fixture
    
    Returns:
        tuple: (controller, mock_view, conflict_model)
    """
    conflict_model = ConflictModel(config_model)
    mock_view = Mock()
    controller = ConflictController(conflict_model, mock_view)
    return controller, mock_view, conflict_model


@pytest.fixture
def course_model(config_model):
    """Create CourseModel for test setup."""
    return CourseModel(config_model)


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def build_test_course(course_id, conflicts=None):
    """Build a simple test course."""
    return CourseConfig(
        course_id=course_id,
        credits=3,
        room=[],
        lab=[],
        faculty=[],
        conflicts=conflicts if conflicts is not None else []
    )


# ================================================================
# TESTS: Add Conflict Workflow
# ================================================================

def test_add_conflict_success(conflict_controller, course_model):
    """
    Test successfully adding a conflict through the controller.
    
    Parameters:
        conflict_controller: Controller fixture (controller, mock_view, model)
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup: Add two courses
    course_a = build_test_course("TEST A")
    course_b = build_test_course("TEST B")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    
    # Mock user selecting two courses
    mock_view.select_course_from_list.side_effect = [
        ("TEST A", 0),  # First course selection
        ("TEST B", 0)   # Second course selection
    ]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_conflict()
    
    # Verify
    assert model.conflict_exists("TEST A", "TEST B") == True
    mock_view.display_message.assert_called()


def test_add_conflict_self_conflict_rejected(conflict_controller, course_model):
    """
    Test that adding a self-conflict is rejected.
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup
    course_a = build_test_course("SELF TEST")
    course_model.add_course(course_a)
    
    # Mock selecting same course twice
    mock_view.select_course_from_list.return_value = ("SELF TEST", 0)
    
    # Execute
    controller.add_conflict()
    
    # Verify error displayed
    mock_view.display_error.assert_called()
    # Conflict should NOT exist
    assert model.conflict_exists("SELF TEST", "SELF TEST") == False


def test_add_conflict_user_cancels(conflict_controller, course_model):
    """
    Test canceling conflict addition.
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup
    course_a = build_test_course("CANCEL A")
    course_b = build_test_course("CANCEL B")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    
    # Mock selections
    mock_view.select_course_from_list.side_effect = [
        ("CANCEL A", 0),
        ("CANCEL B", 0)
    ]
    mock_view.confirm.return_value = False  # User cancels
    
    # Execute
    controller.add_conflict()
    
    # Verify conflict NOT added
    assert model.conflict_exists("CANCEL A", "CANCEL B") == False


# ================================================================
# TESTS: Delete Conflict Workflow
# ================================================================

def test_delete_conflict_success(conflict_controller, course_model):
    """
    Test successfully deleting a conflict.
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup: Add courses and conflict
    course_a = build_test_course("DEL A")
    course_b = build_test_course("DEL B")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    model.add_conflict("DEL A", "DEL B")
    
    # Mock user selecting conflict to delete
    mock_view.display_numbered_conflicts.return_value = None
    mock_view.get_integer_input.return_value = 0  # Select first conflict
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_conflict()
    
    # Verify
    assert model.conflict_exists("DEL A", "DEL B") == False
    mock_view.display_message.assert_called()


def test_delete_existing_conflict(conflict_controller, course_model):
    """
    Test deleting a conflict that exists (from old test).
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup: Add courses with conflict
    course_a = build_test_course("CMSC 140")
    course_b = build_test_course("CMSC 161")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    model.add_conflict("CMSC 140", "CMSC 161")
    
    # Verify conflict exists
    assert model.conflict_exists("CMSC 140", "CMSC 161") == True
    
    # Mock user selecting courses to delete conflict
    mock_view.select_course_from_list.side_effect = [
        ("CMSC 140", 0),
        ("CMSC 161", 0)
    ]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_conflict()
    
    # Reload and verify both directions removed
    model.config_model.reload()
    course_a_updated = course_model.get_course_by_id("CMSC 140")
    course_b_updated = course_model.get_course_by_id("CMSC 161")
    
    assert "CMSC 161" not in course_a_updated.conflicts
    assert "CMSC 140" not in course_b_updated.conflicts


def test_delete_conflict_reversed_order(conflict_controller, course_model):
    """
    Test that order of course selection doesn't matter.
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup
    course_a = build_test_course("CMSC 140")
    course_b = build_test_course("CMSC 161")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    model.add_conflict("CMSC 140", "CMSC 161")
    
    # Mock user selecting in reverse order
    mock_view.select_course_from_list.side_effect = [
        ("CMSC 161", 0),  # Reversed
        ("CMSC 140", 0)
    ]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_conflict()
    
    # Verify conflict deleted
    assert model.conflict_exists("CMSC 140", "CMSC 161") == False


def test_delete_conflict_user_cancels(conflict_controller, course_model):
    """
    Test that canceling preserves the conflict.
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup
    course_a = build_test_course("CMSC 140")
    course_b = build_test_course("CMSC 161")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    model.add_conflict("CMSC 140", "CMSC 161")
    
    # Mock user canceling
    mock_view.select_course_from_list.side_effect = [
        ("CMSC 140", 0),
        ("CMSC 161", 0)
    ]
    mock_view.confirm.return_value = False  # User cancels
    
    # Execute
    controller.delete_conflict()
    
    # Verify conflict still exists
    assert model.conflict_exists("CMSC 140", "CMSC 161") == True


def test_delete_conflict_does_not_exist(conflict_controller, course_model):
    """
    Test attempting to delete a non-existent conflict.
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup: Add courses but NO conflict
    course_a = build_test_course("CMSC 140")
    course_b = build_test_course("CMSC 162")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    # NOTE: No conflict added
    
    # Mock user trying to delete non-existent conflict
    mock_view.select_course_from_list.side_effect = [
        ("CMSC 140", 0),
        ("CMSC 162", 0)
    ]
    
    # Execute
    controller.delete_conflict()
    
    # Verify error message displayed
    mock_view.display_error.assert_called()


def test_delete_conflict_no_conflicts_exist(conflict_controller):
    """
    Test error when no conflicts exist at all.
    
    Parameters:
        conflict_controller: Controller fixture
    """
    controller, mock_view, model = conflict_controller
    
    # Execute (no conflicts in config)
    controller.delete_conflict()
    
    # Verify error message
    mock_view.display_error.assert_called()


# ================================================================
# TESTS: Modify Conflict Workflow
# ================================================================

def test_modify_conflict_mode_1_success(conflict_controller, course_model):
    """
    Test modifying conflict in mode 1 (replace left side).
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup: Add three courses with A-B conflict
    course_a = build_test_course("MOD A")
    course_b = build_test_course("MOD B")
    course_c = build_test_course("MOD C")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    course_model.add_course(course_c)
    model.add_conflict("MOD A", "MOD B")
    
    # Mock user selections
    mock_view.select_course_from_list.side_effect = [
        ("MOD A", 0),  # Select course with conflict
        ("MOD C", 0)   # Select new course
    ]
    mock_view.select_conflict_from_list.return_value = ("MOD B", 0)
    mock_view.get_modification_mode.return_value = 1  # Mode 1
    
    # Execute
    controller.modify_conflict()
    
    # Verify: A-B becomes C-B
    config_model = model.config_model
    config_model.reload()
    assert model.conflict_exists("MOD A", "MOD B") == False
    assert model.conflict_exists("MOD C", "MOD B") == True


# ================================================================
# TESTS: Error Handling
# ================================================================

def test_add_conflict_no_courses_available(conflict_controller):
    """
    Test error when no courses exist.
    
    Parameters:
        conflict_controller: Controller fixture
    """
    controller, mock_view, model = conflict_controller
    
    # Execute (no courses added)
    controller.add_conflict()
    
    # Verify error message shown
    mock_view.display_error.assert_called()


def test_add_conflict_only_one_course(conflict_controller, course_model):
    """
    Test error when only one course exists.
    
    Parameters:
        conflict_controller: Controller fixture
        course_model: Course model for setup
    """
    controller, mock_view, model = conflict_controller
    
    # Setup: Only one course
    course_a = build_test_course("ONLY ONE")
    course_model.add_course(course_a)
    
    # Execute
    controller.add_conflict()
    
    # Verify error message
    mock_view.display_error.assert_called()