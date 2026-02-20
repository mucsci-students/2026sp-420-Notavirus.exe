# tests/test_models/test_room_model.py
"""
Unit tests for RoomModel using MVC architecture.

Tests cover:
- RoomModel CRUD operations (add, delete, modify)
- Room existence checking
- Room reference cleanup in courses and faculty
"""

import pytest
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.room_model import RoomModel
from models.course_model import CourseModel
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
def room_model(test_config):
    """
    Create a RoomModel with test configuration.
    
    Parameters:
        test_config (str): Path to test config (from test_config fixture)
    
    Returns:
        RoomModel: Initialized room model
    """
    config_model = ConfigModel(test_config)
    return RoomModel(config_model)


# ================================================================
# TESTS: Add Room
# ================================================================

def test_add_room_success(room_model):
    """
    Test successfully adding a new room.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    result = room_model.add_room("Roddy 141")
    
    assert result == True
    assert room_model.room_exists("Roddy 141") == True


def test_add_room_duplicate(room_model):
    """
    Test that adding a duplicate room fails.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add first room
    room_model.add_room("Test Room")
    
    # Try to add duplicate
    result = room_model.add_room("Test Room")
    
    assert result == False


def test_add_room_empty_string(room_model):
    """
    Test that adding an empty string fails.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    result = room_model.add_room("")
    
    assert result == False


def test_add_room_whitespace_only(room_model):
    """
    Test that adding whitespace-only string fails.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    result = room_model.add_room("   ")
    
    assert result == False


def test_add_existing_room_from_config(room_model):
    """
    Test that adding a room that already exists in example.json fails.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Roddy 140 exists in example.json
    result = room_model.add_room("Roddy 140")
    
    assert result == False


# ================================================================
# TESTS: Delete Room
# ================================================================

def test_delete_room_success(room_model):
    """
    Test successfully deleting a room.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add test room
    room_model.add_room("Delete Me")
    
    # Delete it
    result = room_model.delete_room("Delete Me")
    
    assert result == True
    assert room_model.room_exists("Delete Me") == False


def test_delete_room_not_found(room_model):
    """
    Test deleting a non-existent room fails.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    result = room_model.delete_room("NonExistent Room")
    
    assert result == False


def test_delete_room_removes_from_courses(room_model):
    """
    Test that deleting a room removes it from courses.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add room and course that uses it
    room_model.add_room("TestRoom 101")
    
    config_model = room_model.config_model
    course = CourseConfig(
        course_id="TEST 101",
        credits=3,
        room=["TestRoom 101"],
        lab=[],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course)
    config_model.safe_save()
    config_model.reload()
    
    # Delete room
    room_model.delete_room("TestRoom 101")
    
    # Verify room removed from course
    updated_course = [c for c in config_model.config.config.courses if c.course_id == "TEST 101"][0]
    assert "TestRoom 101" not in updated_course.room


def test_delete_room_removes_from_faculty_preferences(room_model):
    """
    Test that deleting a room removes it from faculty preferences.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add room and faculty with preference
    room_model.add_room("PrefRoom 101")
    
    config_model = room_model.config_model
    faculty = FacultyConfig(
        name="Test Faculty",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={"PrefRoom 101": 5},
        lab_preferences={},
        maximum_days=5,
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    config_model.config.config.faculty.append(faculty)
    config_model.safe_save()
    config_model.reload()
    
    # Delete room
    room_model.delete_room("PrefRoom 101")
    
    # Verify room removed from faculty preferences
    updated_faculty = [f for f in config_model.config.config.faculty if f.name == "Test Faculty"][0]
    assert "PrefRoom 101" not in updated_faculty.room_preferences


def test_delete_room_no_rooms_exist(room_model):
    """
    Test deleting when no rooms exist.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Clear all rooms first
    all_rooms = room_model.get_all_rooms().copy()
    for room in all_rooms:
        room_model.delete_room(room)
    
    # Try to delete non-existent room
    result = room_model.delete_room("Any Room")
    
    assert result == False


# ================================================================
# TESTS: Modify Room
# ================================================================

def test_modify_room_success(room_model):
    """
    Test successfully modifying a room name.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add test room
    room_model.add_room("OldRoom 101")
    
    # Modify it
    result = room_model.modify_room("OldRoom 101", "NewRoom 101")
    
    assert result == True
    assert room_model.room_exists("OldRoom 101") == False
    assert room_model.room_exists("NewRoom 101") == True


def test_modify_room_not_found(room_model):
    """
    Test modifying a non-existent room fails.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    result = room_model.modify_room("NonExistent", "NewName")
    
    assert result == False


def test_modify_room_new_name_exists(room_model):
    """
    Test modifying to an existing room name fails.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add two rooms
    room_model.add_room("Room A")
    room_model.add_room("Room B")
    
    # Try to rename Room A to Room B (which already exists)
    result = room_model.modify_room("Room A", "Room B")
    
    assert result == False


def test_modify_room_updates_courses(room_model):
    """
    Test that modifying a room updates course references.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add room and course
    room_model.add_room("OldCourseRoom")
    
    config_model = room_model.config_model
    course = CourseConfig(
        course_id="UPDATE 101",
        credits=3,
        room=["OldCourseRoom"],
        lab=[],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course)
    config_model.safe_save()
    config_model.reload()
    
    # Modify room
    room_model.modify_room("OldCourseRoom", "NewCourseRoom")
    
    # Verify course updated
    updated_course = [c for c in config_model.config.config.courses if c.course_id == "UPDATE 101"][0]
    assert "OldCourseRoom" not in updated_course.room
    assert "NewCourseRoom" in updated_course.room


def test_modify_room_updates_faculty_preferences(room_model):
    """
    Test that modifying a room updates faculty preferences.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add room and faculty
    room_model.add_room("OldFacRoom")
    
    config_model = room_model.config_model
    faculty = FacultyConfig(
        name="Update Faculty",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={"OldFacRoom": 8},
        lab_preferences={},
        maximum_days=5,
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    config_model.config.config.faculty.append(faculty)
    config_model.safe_save()
    config_model.reload()
    
    # Modify room
    room_model.modify_room("OldFacRoom", "NewFacRoom")
    
    # Verify faculty updated
    updated_faculty = [f for f in config_model.config.config.faculty if f.name == "Update Faculty"][0]
    assert "OldFacRoom" not in updated_faculty.room_preferences
    assert "NewFacRoom" in updated_faculty.room_preferences
    assert updated_faculty.room_preferences["NewFacRoom"] == 8  # Weight preserved


def test_modify_room_no_conflicts(room_model):
    """
    Test modifying a room without conflicts works.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add a room not used anywhere
    room_model.add_room("Roddy 150")
    
    # Modify it
    result = room_model.modify_room("Roddy 150", "Roddy 151")
    
    assert result == True
    assert room_model.room_exists("Roddy 151") == True


# ================================================================
# TESTS: Room Existence and Retrieval
# ================================================================

def test_room_exists_true(room_model):
    """
    Test room_exists returns True for existing room.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    room_model.add_room("Exists Room")
    
    assert room_model.room_exists("Exists Room") == True


def test_room_exists_false(room_model):
    """
    Test room_exists returns False for non-existent room.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    assert room_model.room_exists("NonExistent Room") == False


def test_get_all_rooms(room_model):
    """
    Test retrieving all rooms.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    all_rooms = room_model.get_all_rooms()
    
    assert isinstance(all_rooms, list)
    assert len(all_rooms) > 0  # example.json should have rooms


def test_get_affected_courses(room_model):
    """
    Test getting courses affected by a room.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add room and courses
    room_model.add_room("Affected Room")
    
    config_model = room_model.config_model
    course1 = CourseConfig(
        course_id="AFF 101",
        credits=3,
        room=["Affected Room"],
        lab=[],
        faculty=[],
        conflicts=[]
    )
    course2 = CourseConfig(
        course_id="AFF 102",
        credits=3,
        room=["Other Room"],
        lab=[],
        faculty=[],
        conflicts=[]
    )
    config_model.config.config.courses.append(course1)
    config_model.config.config.courses.append(course2)
    config_model.safe_save()
    config_model.reload()
    
    # Get affected courses
    affected = room_model.get_affected_courses("Affected Room")
    
    assert len(affected) == 1
    assert affected[0].course_id == "AFF 101"


def test_get_affected_faculty(room_model):
    """
    Test getting faculty affected by a room.
    
    Parameters:
        room_model (RoomModel): Room model fixture
    """
    # Add room and faculty
    room_model.add_room("Pref Room")
    
    config_model = room_model.config_model
    faculty1 = FacultyConfig(
        name="Faculty A",
        maximum_credits=12,
        minimum_credits=0,
        unique_course_limit=2,
        course_preferences={},
        room_preferences={"Pref Room": 5},
        lab_preferences={},
        maximum_days=5,
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )
    faculty2 = FacultyConfig(
        name="Faculty B",
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
    affected = room_model.get_affected_faculty("Pref Room")
    
    assert len(affected) == 1
    assert affected[0].name == "Faculty A"