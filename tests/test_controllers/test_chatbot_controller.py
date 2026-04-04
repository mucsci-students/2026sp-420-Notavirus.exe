# tests/test_controllers/test_chatbot_controller.py
"""
Unit tests for ChatbotController.

Tests cover:
- requires_config decorator behavior
- _no_config() check
- _parse_times() static method
- All tool methods with mocked models
- save_config() success and failure
"""

import pytest
from unittest.mock import Mock
from controllers.chatbot_controller import ChatbotController


# ================================================================
# PYTEST FIXTURES
# ================================================================


@pytest.fixture
def mock_models():
    """Create mock models for testing."""
    return {
        "lab_model": Mock(),
        "room_model": Mock(),
        "course_model": Mock(),
        "faculty_model": Mock(),
        "conflict_model": Mock(),
    }


@pytest.fixture
def controller(mock_models):
    """Create a ChatbotController with mock models."""
    return ChatbotController(
        lab_model=mock_models["lab_model"],
        room_model=mock_models["room_model"],
        course_model=mock_models["course_model"],
        faculty_model=mock_models["faculty_model"],
        conflict_model=mock_models["conflict_model"],
    )


@pytest.fixture
def no_config_controller():
    """Create a ChatbotController with no config loaded (all None)."""
    return ChatbotController(None, None, None, None, None)


# ================================================================
# TESTS: _no_config()
# ================================================================


def test_no_config_true_when_lab_model_is_none(no_config_controller):
    """_no_config() should return True when lab_model is None."""
    assert no_config_controller._no_config() is True


def test_no_config_false_when_lab_model_is_set(controller):
    """_no_config() should return False when lab_model is set."""
    assert controller._no_config() is False


# ================================================================
# TESTS: requires_config decorator
# ================================================================


def test_requires_config_blocks_when_no_config(no_config_controller):
    """Every tool method should return the no-config message when no config is loaded."""
    assert no_config_controller._add_lab("Linux") == "No configuration loaded."
    assert no_config_controller._delete_lab("Linux") == "No configuration loaded."
    assert no_config_controller._get_labs() == "No configuration loaded."
    assert no_config_controller._add_room("Roddy 140") == "No configuration loaded."
    assert no_config_controller._delete_room("Roddy 140") == "No configuration loaded."
    assert no_config_controller._get_rooms() == "No configuration loaded."
    assert no_config_controller._get_courses() == "No configuration loaded."
    assert no_config_controller._get_faculty() == "No configuration loaded."
    assert no_config_controller._get_conflicts() == "No configuration loaded."


def test_requires_config_allows_call_when_config_loaded(controller, mock_models):
    """Tool methods should execute normally when config is loaded."""
    mock_models["lab_model"].get_all_labs.return_value = []
    result = controller._get_labs()
    assert result == "No labs configured."
    mock_models["lab_model"].get_all_labs.assert_called_once()


# ================================================================
# TESTS: _parse_times()
# ================================================================


def test_parse_times_single_day():
    """_parse_times() should parse a single day correctly."""
    result = ChatbotController._parse_times("MON:08:00-17:00")
    assert "MON" in result
    assert len(result["MON"]) == 1
    assert result["MON"][0].start == "08:00"
    assert result["MON"][0].end == "17:00"


def test_parse_times_multiple_days():
    """_parse_times() should parse multiple days correctly."""
    result = ChatbotController._parse_times(
        "MON:08:00-17:00,WED:09:00-18:00,FRI:10:00-15:00"
    )
    assert "MON" in result
    assert "WED" in result
    assert "FRI" in result


def test_parse_times_empty_string():
    """_parse_times() should return empty dict for empty string."""
    result = ChatbotController._parse_times("")
    assert result == {}


def test_parse_times_invalid_entry_skipped():
    """_parse_times() should skip entries without a colon."""
    result = ChatbotController._parse_times("INVALID,MON:08:00-17:00")
    assert "MON" in result
    assert "INVALID" not in result


def test_parse_times_days_uppercased():
    """_parse_times() should uppercase day names."""
    result = ChatbotController._parse_times("mon:08:00-17:00")
    assert "MON" in result


# ================================================================
# TESTS: Lab tool methods
# ================================================================


def test_add_lab_success(controller, mock_models):
    mock_models["lab_model"].add_lab.return_value = True
    result = controller._add_lab("Linux")
    assert result == "Lab 'Linux' added."


def test_add_lab_failure(controller, mock_models):
    mock_models["lab_model"].add_lab.return_value = False
    result = controller._add_lab("Linux")
    assert "Failed" in result
    assert "Linux" in result


def test_delete_lab_success(controller, mock_models):
    mock_models["lab_model"].delete_lab.return_value = True
    result = controller._delete_lab("Linux")
    assert result == "Lab 'Linux' deleted."


def test_delete_lab_failure(controller, mock_models):
    mock_models["lab_model"].delete_lab.return_value = False
    result = controller._delete_lab("Linux")
    assert "Failed" in result


def test_rename_lab_success(controller, mock_models):
    mock_models["lab_model"].modify_lab.return_value = True
    result = controller._rename_lab("Linux", "Mac Lab")
    assert "renamed" in result
    assert "Linux" in result
    assert "Mac Lab" in result


def test_rename_lab_failure(controller, mock_models):
    mock_models["lab_model"].modify_lab.return_value = False
    result = controller._rename_lab("Linux", "Mac Lab")
    assert "Failed" in result


def test_get_labs_with_labs(controller, mock_models):
    mock_models["lab_model"].get_all_labs.return_value = ["Linux", "Mac Lab"]
    result = controller._get_labs()
    assert "Linux" in result
    assert "Mac Lab" in result


def test_get_labs_empty(controller, mock_models):
    mock_models["lab_model"].get_all_labs.return_value = []
    result = controller._get_labs()
    assert result == "No labs configured."


# ================================================================
# TESTS: Room tool methods
# ================================================================


def test_add_room_success(controller, mock_models):
    mock_models["room_model"].add_room.return_value = True
    result = controller._add_room("Roddy 140")
    assert result == "Room 'Roddy 140' added."


def test_add_room_failure(controller, mock_models):
    mock_models["room_model"].add_room.return_value = False
    result = controller._add_room("Roddy 140")
    assert "Failed" in result


def test_delete_room_success(controller, mock_models):
    mock_models["room_model"].delete_room.return_value = True
    result = controller._delete_room("Roddy 140")
    assert result == "Room 'Roddy 140' deleted"


def test_delete_room_failure(controller, mock_models):
    mock_models["room_model"].delete_room.return_value = False
    mock_models["room_model"].get_all_rooms.return_value = []
    result = controller._delete_room("Roddy 140")
    assert "Failed" in result


def test_rename_room_success(controller, mock_models):
    mock_models["room_model"].modify_room.return_value = True
    result = controller._rename_room("Roddy 140", "Roddy 141")
    assert "renamed" in result


def test_rename_room_failure(controller, mock_models):
    mock_models["room_model"].modify_room.return_value = False
    mock_models["room_model"].get_all_rooms.return_value = []
    result = controller._rename_room("Roddy 140", "Roddy 141")
    assert "Failed" in result


def test_get_rooms_with_rooms(controller, mock_models):
    mock_models["room_model"].get_all_rooms.return_value = ["Roddy 140", "Roddy 136"]
    result = controller._get_rooms()
    assert "Roddy 140" in result
    assert "Roddy 136" in result


def test_get_rooms_empty(controller, mock_models):
    mock_models["room_model"].get_all_rooms.return_value = []
    result = controller._get_rooms()
    assert result == "No rooms configured."


# ================================================================
# TESTS: Course tool methods
# ================================================================


def test_add_course_success(controller, mock_models):
    mock_models["room_model"].get_all_rooms.return_value = ["Roddy 140"]
    mock_models["lab_model"].get_all_labs.return_value = []
    faculty_mock = Mock()
    faculty_mock.name = "Hardy"
    mock_models["faculty_model"].get_all_faculty.return_value = [faculty_mock]
    mock_models["course_model"].add_course.return_value = True
    result = controller._add_course("CMSC 340", 3, "Roddy 140", "", "Hardy")
    assert "CMSC 340" in result
    assert "added" in result


def test_delete_course_success(controller, mock_models):
    mock_models["course_model"].delete_course.return_value = True
    result = controller._delete_course("CMSC 340")
    assert "deleted" in result


def test_delete_course_failure(controller, mock_models):
    mock_models["course_model"].delete_course.return_value = False
    result = controller._delete_course("CMSC 340")
    assert "Failed" in result


def test_modify_course_invalid_field(controller, mock_models):
    result = controller._modify_course("CMSC 340", "invalid_field", "value")
    assert "Invalid field" in result


def test_get_courses_with_courses(controller, mock_models):
    course = Mock()
    course.course_id = "CMSC 340"
    mock_models["course_model"].get_all_courses.return_value = [course]
    result = controller._get_courses()
    assert "CMSC 340" in result


def test_get_courses_empty(controller, mock_models):
    mock_models["course_model"].get_all_courses.return_value = []
    result = controller._get_courses()
    assert result == "No courses configured."


def test_get_course_details_not_found(controller, mock_models):
    mock_models["course_model"].get_course_by_id.return_value = None
    result = controller._get_course_details("CMSC 999")
    assert "not found" in result


# ================================================================
# TESTS: Faculty tool methods
# ================================================================


def test_add_faculty_success(controller, mock_models):
    mock_models["faculty_model"].add_faculty.return_value = True
    result = controller._add_faculty(
        "Hardy", True, 5, "MON:08:00-17:00,WED:08:00-17:00"
    )
    assert "Hardy" in result
    assert "added" in result


def test_add_faculty_invalid_times(controller, mock_models):
    result = controller._add_faculty("Hardy", True, 5, "")
    assert "invalid" in result.lower()


def test_delete_faculty_success(controller, mock_models):
    mock_models["faculty_model"].delete_faculty.return_value = True
    result = controller._delete_faculty("Hardy")
    assert "deleted" in result


def test_delete_faculty_failure(controller, mock_models):
    mock_models["faculty_model"].delete_faculty.return_value = False
    mock_models["faculty_model"].get_all_faculty.return_value = []
    result = controller._delete_faculty("Hardy")
    assert "Failed" in result


def test_modify_faculty_invalid_field(controller, mock_models):
    result = controller._modify_faculty("Hardy", "invalid_field", 10)
    assert "Invalid field" in result


def test_modify_faculty_success(controller, mock_models):
    mock_models["faculty_model"].modify_faculty.return_value = True
    result = controller._modify_faculty("Hardy", "maximum_credits", 12)
    assert "updated" in result


def test_get_faculty_with_faculty(controller, mock_models):
    f = Mock()
    f.name = "Hardy"
    mock_models["faculty_model"].get_all_faculty.return_value = [f]
    result = controller._get_faculty()
    assert "Hardy" in result


def test_get_faculty_empty(controller, mock_models):
    mock_models["faculty_model"].get_all_faculty.return_value = []
    result = controller._get_faculty()
    assert result == "No faculty configured."


def test_get_faculty_details_not_found(controller, mock_models):
    mock_models["faculty_model"].get_faculty_by_name.return_value = None
    result = controller._get_faculty_details("Nobody")
    assert "not found" in result


# ================================================================
# TESTS: Conflict tool methods
# ================================================================


def test_add_conflict_success(controller, mock_models):
    mock_models["conflict_model"].add_conflict.return_value = True
    result = controller._add_conflict("CMSC 340", "CMSC 341")
    assert "added" in result
    assert "CMSC 340" in result
    assert "CMSC 341" in result


def test_add_conflict_failure(controller, mock_models):
    mock_models["conflict_model"].add_conflict.return_value = False
    result = controller._add_conflict("CMSC 340", "CMSC 341")
    assert "Failed" in result


def test_delete_conflict_success(controller, mock_models):
    mock_models["conflict_model"].delete_conflict.return_value = True
    result = controller._delete_conflict("CMSC 340", "CMSC 341")
    assert "removed" in result


def test_delete_conflict_failure(controller, mock_models):
    mock_models["conflict_model"].delete_conflict.return_value = False
    result = controller._delete_conflict("CMSC 340", "CMSC 341")
    assert "Failed" in result


def test_get_conflicts_with_conflicts(controller, mock_models):
    mock_models["conflict_model"].get_all_conflicts.return_value = [
        ("CMSC 340", "CMSC 341", 0, 1)
    ]
    result = controller._get_conflicts()
    assert "CMSC 340" in result
    assert "CMSC 341" in result


def test_get_conflicts_empty(controller, mock_models):
    mock_models["conflict_model"].get_all_conflicts.return_value = []
    result = controller._get_conflicts()
    assert result == "No conflicts configured."


# ================================================================
# TESTS: save_config()
# ================================================================


def test_save_config_success(controller, mock_models):
    mock_models["lab_model"].config_model.safe_save.return_value = True
    result = controller.save_config()
    assert result is True


def test_save_config_failure_returns_false(controller, mock_models):
    mock_models["lab_model"].config_model.safe_save.side_effect = Exception(
        "disk error"
    )
    result = controller.save_config()
    assert result is False


def test_save_config_no_config(no_config_controller):
    """save_config() should return False gracefully when no config is loaded."""
    result = no_config_controller.save_config()
    assert result is False
