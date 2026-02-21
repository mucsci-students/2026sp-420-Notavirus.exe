# tests/test_controllers/test_room_controller.py
"""
Unit tests for RoomController using MVC architecture.

Tests cover:
- RoomController workflow orchestration
- View interaction (mocked)
- Model coordination
- Room addition and deletion workflows
"""

import pytest
from unittest.mock import Mock
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.room_model import RoomModel
from controllers.room_controller import RoomController
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
def room_controller(config_model):
    """
    Create RoomController with mocked view.
    
    Returns:
        tuple: (controller, mock_view, room_model)
    """
    room_model = RoomModel(config_model)
    mock_view = Mock()
    controller = RoomController(room_model, mock_view)
    return controller, mock_view, room_model


# ================================================================
# TESTS: Add Room Workflow
# ================================================================

def test_add_room_success(room_controller):
    """
    Test successfully adding a new room.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Mock user input
    mock_view.get_room_name.return_value = "Roddy 141"
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_room()
    
    # Verify
    assert model.room_exists("Roddy 141") == True
    mock_view.display_message.assert_called()


def test_add_room_duplicate(room_controller):
    """
    Test that adding duplicate room fails.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup: Add room first
    model.add_room("Roddy 140")
    
    # Mock user trying to add duplicate
    mock_view.get_room_name.return_value = "Roddy 140"
    
    # Execute
    controller.add_room()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


def test_add_room_user_cancels(room_controller):
    """
    Test canceling room addition.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Mock user input then cancel
    mock_view.get_room_name.return_value = "Cancel Room"
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.add_room()
    
    # Verify not added
    assert model.room_exists("Cancel Room") == False


# ================================================================
# TESTS: Delete Room Workflow
# ================================================================

def test_delete_room_success(room_controller):
    """
    Test successfully deleting a room.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup
    model.add_room("RoomA")
    
    # Mock user selecting and confirming deletion
    mock_view.select_room_from_list.return_value = ("RoomA", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_room()
    
    # Verify deleted
    assert model.room_exists("RoomA") == False
    mock_view.display_message.assert_called()


def test_delete_room_no_rooms_exist(room_controller):
    """
    Test error when there are no rooms.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Clear all rooms
    all_rooms = model.get_all_rooms().copy()
    for room in all_rooms:
        model.delete_room(room)
    
    # Execute
    controller.delete_room()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


def test_delete_room_not_found(room_controller):
    """
    Test error when room doesn't exist.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup: Add some rooms
    model.add_room("RoomA")
    model.add_room("RoomB")
    
    # Mock view returning empty list (room not in list)
    mock_view.get_all_rooms.return_value = []
    
    # Execute
    controller.delete_room()
    
    # Verify handled appropriately
    # Controller should check if rooms exist first


def test_delete_room_user_cancels(room_controller):
    """
    Test canceling room deletion.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup
    model.add_room("RoomA")
    
    # Mock user canceling
    mock_view.select_room_from_list.return_value = ("RoomA", 0)
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.delete_room()
    
    # Verify room still exists
    assert model.room_exists("RoomA") == True


def test_delete_room_removes_from_courses(room_controller):
    """
    Test that deleting a room removes it from courses.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup: Add room and courses using it
    model.add_room("RoomA")
    
    config_model = model.config_model
    course1 = CourseConfig(
        course_id="TEST 101",
        credits=3,
        room=["RoomA", "RoomB"],
        lab=[],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course1)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user deleting room
    mock_view.select_room_from_list.return_value = ("RoomA", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_room()
    
    # Verify room removed from course
    config_model.reload()
    test_course = next((c for c in config_model.config.config.courses if c.course_id == "TEST 101"), None)
    
    if test_course:
        assert "RoomA" not in test_course.room
        assert "RoomB" in test_course.room  # Other room preserved


def test_delete_room_removes_from_faculty_preferences(room_controller):
    """
    Test that deleting a room removes it from faculty preferences.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup: Add room and faculty with preference
    model.add_room("RoomA")
    
    config_model = model.config_model
    faculty = FacultyConfig(
        name="Test Faculty",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={"RoomA": 5, "RoomC": 3},
        lab_preferences={},
        maximum_days=5,
        mandatory_days=[],
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    config_model.config.config.faculty.append(faculty)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user deleting room
    mock_view.select_room_from_list.return_value = ("RoomA", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_room()
    
    # Verify room removed from faculty preferences
    config_model.reload()
    test_faculty = next((f for f in config_model.config.config.faculty if f.name == "Test Faculty"), None)
    
    if test_faculty:
        assert "RoomA" not in test_faculty.room_preferences
        assert test_faculty.room_preferences.get("RoomC") == 3  # Other preference preserved


def test_delete_room_cleanup(room_controller):
    """
    Test full cleanup: room removed from rooms list, courses, and faculty.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup: Room with multiple references
    model.add_room("RoomA")
    
    config_model = model.config_model
    
    # Add course with room
    course = CourseConfig(
        course_id="CLEANUP 101",
        credits=3,
        room=["RoomA"],
        lab=[],
        faculty=[],
        conflicts=[]
    )
    
    # Add faculty with room preference
    faculty = FacultyConfig(
        name="Cleanup Faculty",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={"RoomA": 5},
        lab_preferences={},
        maximum_days=5,
        mandatory_days=[],
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    
    config_model.config.config.courses.append(course)
    config_model.config.config.faculty.append(faculty)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user deleting room
    mock_view.select_room_from_list.return_value = ("RoomA", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_room()
    
    # Verify complete cleanup
    config_model.reload()
    
    # Room removed from rooms list
    assert "RoomA" not in config_model.config.config.rooms
    
    # Room removed from course
    cleanup_course = next((c for c in config_model.config.config.courses if c.course_id == "CLEANUP 101"), None)
    if cleanup_course:
        assert "RoomA" not in cleanup_course.room
    
    # Room removed from faculty
    cleanup_faculty = next((f for f in config_model.config.config.faculty if f.name == "Cleanup Faculty"), None)
    if cleanup_faculty:
        assert "RoomA" not in cleanup_faculty.room_preferences


# ================================================================
# TESTS: Modify Room Workflow
# ================================================================

def test_modify_room_success(room_controller):
    """
    Test successfully modifying a room name.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup
    model.add_room("OldRoom 101")
    
    # Mock user modifying room
    mock_view.select_room_from_list.return_value = ("OldRoom 101", 0)
    mock_view.get_new_room_name.return_value = "NewRoom 101"
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_room()
    
    # Verify
    assert model.room_exists("OldRoom 101") == False
    assert model.room_exists("NewRoom 101") == True


def test_modify_room_to_existing_name(room_controller):
    """
    Test that modifying to existing room name fails.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup: Add two rooms
    model.add_room("Room A")
    model.add_room("Room B")
    
    # Mock user trying to rename Room A to Room B
    mock_view.select_room_from_list.return_value = ("Room A", 0)
    mock_view.get_new_room_name.return_value = "Room B"
    
    # Execute
    controller.modify_room()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


def test_modify_room_updates_courses(room_controller):
    """
    Test that modifying a room updates course references.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup
    model.add_room("OldRoom")
    
    config_model = model.config_model
    course = CourseConfig(
        course_id="UPDATE 101",
        credits=3,
        room=["OldRoom"],
        lab=[],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course)
    config_model.safe_save()
    config_model.reload()
    
    # Mock user modifying room
    mock_view.select_room_from_list.return_value = ("OldRoom", 0)
    mock_view.get_new_room_name.return_value = "NewRoom"
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_room()
    
    # Verify course updated
    config_model.reload()
    update_course = next((c for c in config_model.config.config.courses if c.course_id == "UPDATE 101"), None)
    
    if update_course:
        assert "OldRoom" not in update_course.room
        assert "NewRoom" in update_course.room


def test_modify_room_user_cancels(room_controller):
    """
    Test canceling room modification.
    
    Parameters:
        room_controller: Controller fixture
    """
    controller, mock_view, model = room_controller
    
    # Setup
    model.add_room("RoomA")
    
    # Mock user canceling
    mock_view.select_room_from_list.return_value = ("RoomA", 0)
    mock_view.get_new_room_name.return_value = "RoomB"
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.modify_room()
    
    # Verify no changes
    assert model.room_exists("RoomA") == True
    assert model.room_exists("RoomB") == False