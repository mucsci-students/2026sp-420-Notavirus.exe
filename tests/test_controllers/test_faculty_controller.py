# tests/test_controllers/test_faculty_controller.py
"""
Unit tests for FacultyController using MVC architecture.

Tests cover:
- FacultyController workflow orchestration
- View interaction (mocked)
- Model coordination
- Faculty modification workflows
"""

import pytest
from unittest.mock import Mock
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.faculty_model import FacultyModel
from controllers.faculty_controller import FacultyController
from scheduler import FacultyConfig, TimeRange

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
def faculty_controller(config_model):
    """
    Create FacultyController with mocked view.
    
    Returns:
        tuple: (controller, mock_view, faculty_model)
    """
    faculty_model = FacultyModel(config_model)
    mock_view = Mock()
    controller = FacultyController(faculty_model, mock_view)
    return controller, mock_view, faculty_model


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def build_test_faculty(name, is_full_time=True, max_credits=12, min_credits=0,
                       max_days=5, course_prefs=None, mandatory_days=None):
    """Build a test faculty member."""
    return FacultyConfig(
        name=name,
        maximum_credits=max_credits,
        minimum_credits=min_credits,
        unique_course_limit=2 if is_full_time else 1,
        course_preferences=course_prefs or {},
        room_preferences={},
        lab_preferences={},
        maximum_days=max_days,
        mandatory_days=mandatory_days or [],
        times={"MON": [TimeRange(start="09:00", end="17:00")]}
    )


# ================================================================
# TESTS: Add Faculty Workflow
# ================================================================

def test_add_faculty_success(faculty_controller):
    """
    Test successfully adding a new faculty member.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Mock user input for new faculty
    mock_view.get_faculty_name.return_value = "Test Faculty"
    mock_view.get_yes_no_input.return_value = True  # Full-time
    mock_view.get_day_selection.return_value = ["MON", "WED", "FRI"]
    mock_view.get_yes_no_input.return_value = True  # Same time all days
    mock_view.get_time_input.side_effect = ["09:00", "17:00"]
    mock_view.get_course_preferences.return_value = {}
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_faculty()
    
    # Verify
    assert model.faculty_exists("Test Faculty") == True
    mock_view.display_message.assert_called()


def test_add_faculty_with_preferences(faculty_controller):
    """
    Test adding faculty with course preferences.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Mock user input
    mock_view.get_faculty_name.return_value = "Pref Faculty"
    mock_view.get_yes_no_input.return_value = True  # Full-time
    mock_view.get_day_selection.return_value = ["MON", "WED", "FRI"]
    mock_view.get_yes_no_input.return_value = True  # Same time
    mock_view.get_time_input.side_effect = ["09:00", "17:00"]
    mock_view.get_course_preferences.return_value = {"CMSC 161": 5}
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_faculty()
    
    # Verify
    faculty = model.get_faculty_by_name("Pref Faculty")
    assert faculty.course_preferences == {"CMSC 161": 5}


def test_add_faculty_duplicate_name(faculty_controller):
    """
    Test that adding duplicate faculty name fails.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Add faculty first
    faculty = build_test_faculty("Hardy")
    model.add_faculty(faculty)
    
    # Mock user trying to add duplicate
    mock_view.get_faculty_name.return_value = "Hardy"
    
    # Execute
    controller.add_faculty()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


def test_add_faculty_user_cancels(faculty_controller):
    """
    Test canceling faculty addition.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Mock user input then cancel
    mock_view.get_faculty_name.return_value = "Cancel Faculty"
    mock_view.get_yes_no_input.return_value = True
    mock_view.get_day_selection.return_value = ["MON"]
    mock_view.get_yes_no_input.return_value = True
    mock_view.get_time_input.side_effect = ["09:00", "17:00"]
    mock_view.get_course_preferences.return_value = {}
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.add_faculty()
    
    # Verify not added
    assert model.faculty_exists("Cancel Faculty") == False


def test_add_adjunct_faculty(faculty_controller):
    """
    Test adding adjunct faculty with correct limits.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Mock user input for adjunct
    mock_view.get_faculty_name.return_value = "Adjunct Faculty"
    mock_view.get_yes_no_input.return_value = False  # Not full-time
    mock_view.get_day_selection.return_value = ["MON", "WED"]
    mock_view.get_yes_no_input.return_value = True
    mock_view.get_time_input.side_effect = ["09:00", "17:00"]
    mock_view.get_course_preferences.return_value = {}
    mock_view.confirm.return_value = True
    
    # Execute
    controller.add_faculty()
    
    # Verify adjunct limits
    faculty = model.get_faculty_by_name("Adjunct Faculty")
    assert faculty.maximum_credits == 4
    assert faculty.unique_course_limit == 1


# ================================================================
# TESTS: Delete Faculty Workflow
# ================================================================

def test_delete_existing_faculty(faculty_controller):
    """
    Test deleting an existing faculty member.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Add two faculty
    faculty1 = build_test_faculty("Kunkle")
    faculty2 = build_test_faculty("Haldeman")
    model.add_faculty(faculty1)
    model.add_faculty(faculty2)
    
    # Mock user selecting Kunkle to delete
    mock_view.select_faculty_from_list.return_value = ("Kunkle", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_faculty()
    
    # Verify
    assert model.faculty_exists("Kunkle") == False
    assert model.faculty_exists("Haldeman") == True
    assert len(model.get_all_faculty()) == 1


def test_delete_case_insensitive(faculty_controller):
    """
    Test deleting with case-insensitive name matching.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Kunkle")
    model.add_faculty(faculty)
    
    # Mock user entering lowercase name
    mock_view.select_faculty_from_list.return_value = ("kunkle", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_faculty()
    
    # Verify (assuming case-insensitive matching in controller)
    assert len(model.get_all_faculty()) == 0


def test_delete_nonexistent_faculty(faculty_controller):
    """
    Test deleting a non-existent faculty member.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Add one faculty
    faculty = build_test_faculty("Kunkle")
    model.add_faculty(faculty)
    
    # Mock user selecting non-existent faculty (should not be in list)
    mock_view.get_all_faculty.return_value = [("Kunkle", 0)]
    
    # Execute - controller should not allow selecting non-existent
    controller.delete_faculty()
    
    # If somehow attempted, verify original faculty still exists
    assert model.faculty_exists("Kunkle") == True


def test_delete_from_empty_list(faculty_controller):
    """
    Test error when trying to delete from empty faculty list.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Execute (no faculty added)
    controller.delete_faculty()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


def test_delete_only_one_faculty(faculty_controller):
    """
    Test deleting the only faculty member.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Add one faculty
    faculty = build_test_faculty("Kunkle")
    model.add_faculty(faculty)
    
    # Mock user confirming deletion
    mock_view.select_faculty_from_list.return_value = ("Kunkle", 0)
    mock_view.confirm.return_value = True
    
    # Execute
    controller.delete_faculty()
    
    # Verify list is empty
    assert len(model.get_all_faculty()) == 0


def test_delete_user_cancels(faculty_controller):
    """
    Test canceling deletion preserves faculty.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Kunkle")
    model.add_faculty(faculty)
    
    # Mock user canceling
    mock_view.select_faculty_from_list.return_value = ("Kunkle", 0)
    mock_view.confirm.return_value = False  # Cancel
    
    # Execute
    controller.delete_faculty()
    
    # Verify faculty still exists
    assert model.faculty_exists("Kunkle") == True


# ================================================================
# TESTS: Modify Faculty - Basic Fields
# ================================================================

def test_modify_max_credits(faculty_controller):
    """
    Test modifying maximum credits.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Add faculty
    faculty = build_test_faculty("Yang", max_credits=12)
    model.add_faculty(faculty)
    
    # Mock user selecting faculty and modifying max credits
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 2  # max credits
    mock_view.get_integer_input.return_value = 14
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify
    updated = model.get_faculty_by_name("Yang")
    assert updated.maximum_credits == 14


def test_modify_min_credits(faculty_controller):
    """
    Test modifying minimum credits.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Yang", min_credits=0)
    model.add_faculty(faculty)
    
    # Mock user input
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 3  # min credits
    mock_view.get_integer_input.return_value = 8
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify
    updated = model.get_faculty_by_name("Yang")
    assert updated.minimum_credits == 8


def test_modify_max_days(faculty_controller):
    """
    Test modifying maximum days.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Yang", max_days=5)
    model.add_faculty(faculty)
    
    # Mock user input
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 5  # max days
    mock_view.get_integer_input.return_value = 3
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify
    updated = model.get_faculty_by_name("Yang")
    assert updated.maximum_days == 3


# ================================================================
# TESTS: Modify Faculty - Position Change
# ================================================================

def test_modify_position_to_adjunct(faculty_controller):
    """
    Test changing position from full-time to adjunct.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Full-time faculty
    faculty = build_test_faculty("Yang", is_full_time=True, max_credits=12)
    model.add_faculty(faculty)
    
    # Mock user changing to adjunct
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 1  # position
    mock_view.get_yes_no_input.return_value = False  # Not full-time
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify adjunct limits applied
    updated = model.get_faculty_by_name("Yang")
    assert updated.maximum_credits == 4
    assert updated.unique_course_limit == 1
    assert updated.minimum_credits <= 4


def test_modify_position_to_fulltime(faculty_controller):
    """
    Test changing position from adjunct to full-time.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Adjunct faculty
    faculty = build_test_faculty("Yang", is_full_time=False, max_credits=4)
    faculty.unique_course_limit = 1
    model.add_faculty(faculty)
    
    # Mock user changing to full-time
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 1  # position
    mock_view.get_yes_no_input.return_value = True  # Full-time
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify full-time limits applied
    updated = model.get_faculty_by_name("Yang")
    assert updated.maximum_credits == 12
    assert updated.unique_course_limit == 2


# ================================================================
# TESTS: Modify Faculty - Preferences
# ================================================================

def test_clear_course_preferences(faculty_controller):
    """
    Test clearing course preferences.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Faculty with preferences
    faculty = build_test_faculty("Yang", course_prefs={"CMSC 161": 5})
    model.add_faculty(faculty)
    
    # Mock user clearing preferences (empty input)
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 7  # course preferences
    mock_view.get_course_preferences.return_value = {}  # Empty dict
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify preferences cleared
    updated = model.get_faculty_by_name("Yang")
    assert updated.course_preferences == {}


# ================================================================
# TESTS: Modify Faculty - Availability Times
# ================================================================

def test_modify_availability_same_time_all_days(faculty_controller):
    """
    Test setting same time for all selected days.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Yang")
    model.add_faculty(faculty)
    
    # Mock user setting same time for M/W/F
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 6  # availability times
    mock_view.get_day_selection.return_value = ["MON", "WED", "FRI"]
    mock_view.get_yes_no_input.return_value = True  # Same time all days
    mock_view.get_time_input.side_effect = ["09:00", "17:00"]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify all days have same time
    updated = model.get_faculty_by_name("Yang")
    for day in ["MON", "WED", "FRI"]:
        assert updated.times[day][0].start == "09:00"
        assert updated.times[day][0].end == "17:00"


def test_modify_availability_different_times_per_day(faculty_controller):
    """
    Test setting different times for each day.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Yang")
    model.add_faculty(faculty)
    
    # Mock user setting different times for M/W
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 6  # availability times
    mock_view.get_day_selection.return_value = ["MON", "WED"]
    mock_view.get_yes_no_input.return_value = False  # Different times
    mock_view.get_time_input.side_effect = [
        "08:00", "12:00",  # Monday
        "13:00", "17:00"   # Wednesday
    ]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify each day has correct time
    updated = model.get_faculty_by_name("Yang")
    assert updated.times["MON"][0].start == "08:00"
    assert updated.times["MON"][0].end == "12:00"
    assert updated.times["WED"][0].start == "13:00"
    assert updated.times["WED"][0].end == "17:00"


def test_no_availability(faculty_controller):
    """
    Test setting no availability (all days empty).
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Yang")
    model.add_faculty(faculty)
    
    # Mock user selecting "none" for availability
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 6  # availability times
    mock_view.get_day_selection.return_value = []  # No days = "none"
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify all days empty
    updated = model.get_faculty_by_name("Yang")
    assert all(updated.times[day] == [] for day in updated.times)


# ================================================================
# TESTS: Modify Faculty - Error Handling
# ================================================================

def test_modify_faculty_not_found(faculty_controller):
    """
    Test error when faculty doesn't exist.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Mock selecting non-existent faculty
    mock_view.get_all_faculty.return_value = []
    
    # Execute
    controller.modify_faculty()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


def test_modify_canceled(faculty_controller):
    """
    Test canceling modification preserves data.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Yang", max_credits=12)
    model.add_faculty(faculty)
    
    # Mock user canceling
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 10  # Exit/cancel
    
    # Execute
    controller.modify_faculty()
    
    # Verify no changes
    updated = model.get_faculty_by_name("Yang")
    assert updated.maximum_credits == 12


def test_max_days_lower_than_mandatory_days_fails(faculty_controller):
    """
    Test that setting max days lower than mandatory days count fails validation.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup: Faculty with 2 mandatory days
    faculty = build_test_faculty("Yang", max_days=4, mandatory_days=["MON", "WED"])
    model.add_faculty(faculty)
    
    # Mock user trying to set max_days to 1 (less than 2 mandatory)
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 5  # max days
    mock_view.get_integer_input.return_value = 1  # Too low!
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify change rejected, original value preserved
    updated = model.get_faculty_by_name("Yang")
    assert updated.maximum_days == 4  # Unchanged


# ================================================================
# TESTS: Modify Faculty - Default Values
# ================================================================

def test_default_times(faculty_controller):
    """
    Test that empty time input defaults to 00:00-23:59.
    
    Parameters:
        faculty_controller: Controller fixture
    """
    controller, mock_view, model = faculty_controller
    
    # Setup
    faculty = build_test_faculty("Yang")
    model.add_faculty(faculty)
    
    # Mock user pressing enter for times (defaults)
    mock_view.select_faculty_from_list.return_value = ("Yang", 0)
    mock_view.get_modification_choice.return_value = 6  # availability
    mock_view.get_day_selection.return_value = ["MON", "WED"]
    mock_view.get_yes_no_input.return_value = False  # Different times
    mock_view.get_time_input.side_effect = [
        "",      # MON start - defaults to 00:00
        "",      # MON end - defaults to 23:59
        "",      # WED start - defaults to 00:00
        ""       # WED end - defaults to 23:59
    ]
    mock_view.confirm.return_value = True
    
    # Execute
    controller.modify_faculty()
    
    # Verify defaults applied
    updated = model.get_faculty_by_name("Yang")
    assert updated.times["MON"][0].start == "00:00"
    assert updated.times["MON"][0].end == "23:59"
    assert updated.times["WED"][0].start == "00:00"
    assert updated.times["WED"][0].end == "23:59"