# tests/test_controllers/test_controllers.py
"""
Smoke tests and functional tests for all sub-controllers.
"""

import pytest
from unittest.mock import Mock, MagicMock
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.faculty_model import FacultyModel
from models.course_model import CourseModel
from models.conflict_model import ConflictModel
from models.lab_model import LabModel
from models.room_model import RoomModel
from models.scheduler_model import SchedulerModel

from controllers.faculty_controller import FacultyController
from controllers.course_controller import CourseController
from controllers.conflict_controller import ConflictController
from controllers.lab_controller import LabController
from controllers.room_controller import RoomController
from controllers.schedule_controller import ScheduleController

TESTING_CONFIG   = "example.json"
TEST_COPY_CONFIG = "test_copy.json"


@pytest.fixture
def test_config():
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def config_model(test_config):
    return ConfigModel(test_config)


@pytest.fixture
def course_controller(config_model):
    course_model = CourseModel(config_model)
    return CourseController(course_model, config_model)


@pytest.fixture
def faculty_controller(config_model):
    faculty_model = FacultyModel(config_model)
    return FacultyController(faculty_model, Mock())


@pytest.fixture
def lab_controller(config_model):
    lab_model = LabModel(config_model)
    return LabController(lab_model, Mock())


@pytest.fixture
def room_controller(config_model):
    room_model = RoomModel(config_model)
    return RoomController(room_model, Mock())


@pytest.fixture
def conflict_controller(config_model):
    conflict_model = ConflictModel(config_model)
    return ConflictController(conflict_model, Mock())


# ================================================================
# SMOKE TESTS: Controller Instantiation
# ================================================================

def test_faculty_controller_instantiation(config_model):
    controller = FacultyController(FacultyModel(config_model), Mock())
    assert controller is not None


def test_course_controller_instantiation(config_model):
    controller = CourseController(CourseModel(config_model), config_model)
    assert controller is not None


def test_conflict_controller_instantiation(config_model):
    controller = ConflictController(ConflictModel(config_model), Mock())
    assert controller is not None


def test_lab_controller_instantiation(config_model):
    controller = LabController(LabModel(config_model), Mock())
    assert controller is not None


def test_room_controller_instantiation(config_model):
    controller = RoomController(RoomModel(config_model), Mock())
    assert controller is not None


def test_schedule_controller_instantiation(config_model):
    """
    ScheduleController takes a SchedulerModel, not a ConfigModel.
    ✅ Fixed: was incorrectly passing config_model before.
    """
    scheduler_model = SchedulerModel(config_model)
    controller      = ScheduleController(scheduler_model, Mock())
    assert controller is not None


# ================================================================
# SMOKE TESTS: Controllers Have Expected Attributes
# ================================================================

def test_faculty_controller_has_model_and_view(config_model):
    controller = FacultyController(FacultyModel(config_model), Mock())
    assert hasattr(controller, 'model')
    assert hasattr(controller, 'view')


def test_course_controller_has_model(config_model):
    controller = CourseController(CourseModel(config_model), config_model)
    assert hasattr(controller, 'model')
    assert hasattr(controller, 'config_model')


def test_conflict_controller_has_model(config_model):
    controller = ConflictController(ConflictModel(config_model), Mock())
    assert hasattr(controller, 'model')
    assert hasattr(controller, 'config_model')


def test_lab_controller_has_model(config_model):
    controller = LabController(LabModel(config_model), Mock())
    assert hasattr(controller, 'model')
    assert hasattr(controller, 'config_model')


def test_room_controller_has_model(config_model):
    controller = RoomController(RoomModel(config_model), Mock())
    assert hasattr(controller, 'model')
    assert hasattr(controller, 'config_model')


# ================================================================
# SMOKE TESTS: Controllers Accept Mock View
# ================================================================

def test_controllers_all_accept_mock_view(config_model):
    mock_view    = Mock()
    scheduler_model = SchedulerModel(config_model)   # ✅ correct type
    controllers  = [
        FacultyController(FacultyModel(config_model), mock_view),
        CourseController(CourseModel(config_model), config_model),
        ConflictController(ConflictModel(config_model), mock_view),
        LabController(LabModel(config_model), mock_view),
        RoomController(RoomModel(config_model), mock_view),
        ScheduleController(scheduler_model, mock_view),
    ]
    assert len(controllers) == 6
    assert all(c is not None for c in controllers)


# ================================================================
# TESTS: CourseController.add_course
# ================================================================

def test_course_controller_add_course_success(course_controller):
    data    = {'course_id': 'TEST 999', 'credits': 3, 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    success, message = course_controller.add_course(data)
    assert success is True
    assert 'TEST 999' in message


def test_course_controller_add_course_missing_id(course_controller):
    """Validation: empty course ID should fail in the Controller."""
    data    = {'course_id': '', 'credits': 3, 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    success, message = course_controller.add_course(data)
    assert success is False
    assert 'required' in message.lower()


def test_course_controller_add_course_invalid_credits(course_controller):
    """Validation: non-numeric credits should fail in the Controller."""
    data    = {'course_id': 'TEST 998', 'credits': 'abc', 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    success, message = course_controller.add_course(data)
    assert success is False
    assert 'credits' in message.lower()


def test_course_controller_add_course_second_section(course_controller):
    data = {'course_id': 'SECT 101', 'credits': 3, 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    course_controller.add_course(data)
    success, message = course_controller.add_course(data)
    assert success is True


def test_course_controller_add_course_zero_credits(course_controller):
    data    = {'course_id': 'ZERO 101', 'credits': 0, 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    success, message = course_controller.add_course(data)
    assert success is True


def test_course_controller_get_available_resources(course_controller):
    resources = course_controller.get_available_resources()
    assert 'rooms'   in resources
    assert 'labs'    in resources
    assert 'faculty' in resources
    assert isinstance(resources['rooms'],   list)
    assert isinstance(resources['labs'],    list)
    assert isinstance(resources['faculty'], list)


# ================================================================
# TESTS: CourseController.modify_course
# ================================================================

def test_modify_course_valid_rooms_labs(course_controller):
    data = {'course_id': 'TEST 101', 'credits': 3, 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    course_controller.add_course(data)
    mods    = {'room': ['Roddy 140'], 'lab': ['Linux'], 'faculty': []}
    success, msg = course_controller.modify_course('TEST 101', 0, mods)
    assert success is True
    assert 'updated successfully' in msg


def test_modify_course_invalid_room(course_controller):
    data = {'course_id': 'TEST 102', 'credits': 3, 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    course_controller.add_course(data)
    success, msg = course_controller.modify_course('TEST 102', 0, {'room': ['InvalidRoom999']})
    assert success is False
    assert 'Invalid room' in msg


def test_modify_course_invalid_lab(course_controller):
    data = {'course_id': 'TEST 103', 'credits': 3, 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    course_controller.add_course(data)
    success, msg = course_controller.modify_course('TEST 103', 0, {'lab': ['InvalidLab999']})
    assert success is False
    assert 'Invalid lab' in msg


def test_modify_course_invalid_faculty(course_controller):
    data = {'course_id': 'TEST 104', 'credits': 3, 'room': [], 'lab': [], 'faculty': [], 'conflicts': []}
    course_controller.add_course(data)
    success, msg = course_controller.modify_course('TEST 104', 0, {'faculty': ['InvalidFaculty999']})
    assert success is False
    assert 'Invalid faculty' in msg


# ================================================================
# TESTS: FacultyController — new GUI methods
# ================================================================

def test_faculty_controller_get_all_faculty(faculty_controller):
    """get_all_faculty() should return a list."""
    result = faculty_controller.get_all_faculty()
    assert isinstance(result, list)


def test_faculty_controller_get_available_courses(faculty_controller):
    """get_available_courses() should return a list of strings."""
    result = faculty_controller.get_available_courses()
    assert isinstance(result, list)
    assert all(isinstance(c, str) for c in result)


def test_faculty_controller_get_available_labs(faculty_controller):
    """get_available_labs() should return a list of strings."""
    result = faculty_controller.get_available_labs()
    assert isinstance(result, list)


def test_faculty_controller_get_available_rooms(faculty_controller):
    """get_available_rooms() should return a list of strings."""
    result = faculty_controller.get_available_rooms()
    assert isinstance(result, list)


def test_faculty_controller_add_faculty_returns_tuple(faculty_controller):
    """add_faculty() should return (bool, str)."""
    data = {
        'name': 'Test Faculty',
        'is_full_time': True,
        'times': {},
        'days': [],
        'course_preferences': {},
        'lab_preferences': {},
    }
    success, message = faculty_controller.add_faculty(data)
    assert isinstance(success, bool)
    assert isinstance(message, str)


def test_faculty_controller_delete_faculty_returns_tuple(faculty_controller):
    """delete_faculty() should return (bool, str)."""
    success, message = faculty_controller.delete_faculty('Nonexistent Person')
    assert isinstance(success, bool)
    assert isinstance(message, str)


def test_faculty_controller_modify_faculty_field_returns_tuple(faculty_controller):
    """modify_faculty_field() should return (bool, str)."""
    success, message = faculty_controller.modify_faculty_field('Nonexistent', 'minimum_credits', 3)
    assert isinstance(success, bool)
    assert isinstance(message, str)


# ================================================================
# TESTS: RoomController — new GUI methods
# ================================================================

def test_room_controller_get_all_rooms(room_controller):
    result = room_controller.get_all_rooms()
    assert isinstance(result, list)


def test_room_controller_add_room_returns_tuple(room_controller):
    success, message = room_controller.add_room('Test Room 101')
    assert isinstance(success, bool)
    assert isinstance(message, str)


def test_room_controller_add_room_empty_name(room_controller):
    """Validation: empty name should fail."""
    success, message = room_controller.add_room('')
    assert success is False


def test_room_controller_delete_room_no_selection(room_controller):
    """Validation: empty selection should fail."""
    success, message = room_controller.delete_room('')
    assert success is False


def test_room_controller_modify_room_empty_new_name(room_controller):
    """Validation: empty new name should fail."""
    success, message = room_controller.modify_room('Roddy 140', '')
    assert success is False


# ================================================================
# TESTS: LabController — new GUI methods
# ================================================================

def test_lab_controller_get_all_labs(lab_controller):
    result = lab_controller.get_all_labs()
    assert isinstance(result, list)


def test_lab_controller_add_lab_returns_tuple(lab_controller):
    success, message = lab_controller.add_lab('Test Lab')
    assert isinstance(success, bool)
    assert isinstance(message, str)


def test_lab_controller_add_lab_empty_name(lab_controller):
    success, message = lab_controller.add_lab('')
    assert success is False


def test_lab_controller_delete_labs_returns_tuple(lab_controller):
    success, message = lab_controller.delete_labs([])
    assert isinstance(success, bool)
    assert isinstance(message, str)


def test_lab_controller_modify_lab_empty_name(lab_controller):
    success, message = lab_controller.modify_lab('Linux', '')
    assert success is False


# ================================================================
# TESTS: ConflictController — new GUI methods
# ================================================================

def test_conflict_controller_get_all_courses(conflict_controller):
    result = conflict_controller.get_all_courses()
    assert isinstance(result, list)


def test_conflict_controller_get_courses_with_sections(conflict_controller):
    result = conflict_controller.get_courses_with_sections()
    assert isinstance(result, list)
    if result:
        label, idx, course = result[0]
        assert isinstance(label, str)
        assert isinstance(idx, int)


def test_conflict_controller_add_conflict_returns_tuple(conflict_controller):
    courses = conflict_controller.get_all_courses()
    if len(courses) >= 2:
        success, message = conflict_controller.add_conflict(
            courses[0].course_id, courses[1].course_id
        )
        assert isinstance(success, bool)
        assert isinstance(message, str)