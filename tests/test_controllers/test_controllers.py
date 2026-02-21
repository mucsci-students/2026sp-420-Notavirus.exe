# tests/test_controllers/test_controllers.py
"""
Minimal smoke tests for controllers.

These tests verify that:
1. Controller classes can be imported
2. Controllers can be instantiated
3. Controllers have expected methods
4. Controllers accept model and view parameters

These are NOT comprehensive workflow tests - just basic sanity checks.
"""

import pytest
from unittest.mock import Mock
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.faculty_model import FacultyModel
from models.course_model import CourseModel
from models.conflict_model import ConflictModel
from models.lab_model import LabModel
from models.room_model import RoomModel

# Import controllers
from controllers.faculty_controller import FacultyController
from controllers.course_controller import CourseController
from controllers.conflict_controller import ConflictController
from controllers.lab_controller import LabController
from controllers.room_controller import RoomController
from controllers.schedule_controller import ScheduleController

# Test configuration
TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_copy.json"


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


# ================================================================
# SMOKE TESTS: Controller Instantiation
# ================================================================

def test_faculty_controller_instantiation(config_model):
    """Test that FacultyController can be instantiated."""
    faculty_model = FacultyModel(config_model)
    mock_view = Mock()
    
    # Should not raise
    controller = FacultyController(faculty_model, mock_view)
    assert controller is not None


def test_course_controller_instantiation(config_model):
    """Test that CourseController can be instantiated."""
    course_model = CourseModel(config_model)
    mock_view = Mock()
    
    # CourseController takes 3 params: course_model, view, config_model
    controller = CourseController(course_model, mock_view, config_model)
    assert controller is not None


def test_conflict_controller_instantiation(config_model):
    """Test that ConflictController can be instantiated."""
    conflict_model = ConflictModel(config_model)
    mock_view = Mock()
    
    # Should not raise
    controller = ConflictController(conflict_model, mock_view)
    assert controller is not None


def test_lab_controller_instantiation(config_model):
    """Test that LabController can be instantiated."""
    lab_model = LabModel(config_model)
    mock_view = Mock()
    
    # Should not raise
    controller = LabController(lab_model, mock_view)
    assert controller is not None


def test_room_controller_instantiation(config_model):
    """Test that RoomController can be instantiated."""
    room_model = RoomModel(config_model)
    mock_view = Mock()
    
    # Should not raise
    controller = RoomController(room_model, mock_view)
    assert controller is not None


def test_schedule_controller_instantiation(config_model):
    """Test that ScheduleController can be instantiated."""
    mock_view = Mock()
    
    # Should not raise
    controller = ScheduleController(config_model, mock_view)
    assert controller is not None


# ================================================================
# SMOKE TESTS: Controller Has Expected Methods
# ================================================================

def test_faculty_controller_has_methods(config_model):
    """Test that FacultyController has expected methods."""
    faculty_model = FacultyModel(config_model)
    mock_view = Mock()
    controller = FacultyController(faculty_model, mock_view)
    
    # Check for common method names (adjust based on your actual controllers)
    # Just checking they exist, not calling them
    assert hasattr(controller, 'faculty_model') or hasattr(controller, 'model')
    assert hasattr(controller, 'view') or hasattr(controller, 'cli_view')


def test_course_controller_has_methods(config_model):
    """Test that CourseController has expected methods."""
    course_model = CourseModel(config_model)
    mock_view = Mock()
    controller = CourseController(course_model, mock_view, config_model)
    
    assert hasattr(controller, 'course_model') or hasattr(controller, 'model')
    assert hasattr(controller, 'view') or hasattr(controller, 'cli_view')


def test_conflict_controller_has_methods(config_model):
    """Test that ConflictController has expected methods."""
    conflict_model = ConflictModel(config_model)
    mock_view = Mock()
    controller = ConflictController(conflict_model, mock_view)
    
    assert hasattr(controller, 'conflict_model') or hasattr(controller, 'model')
    assert hasattr(controller, 'view') or hasattr(controller, 'cli_view')


def test_lab_controller_has_methods(config_model):
    """Test that LabController has expected methods."""
    lab_model = LabModel(config_model)
    mock_view = Mock()
    controller = LabController(lab_model, mock_view)
    
    assert hasattr(controller, 'lab_model') or hasattr(controller, 'model')
    assert hasattr(controller, 'view') or hasattr(controller, 'cli_view')


def test_room_controller_has_methods(config_model):
    """Test that RoomController has expected methods."""
    room_model = RoomModel(config_model)
    mock_view = Mock()
    controller = RoomController(room_model, mock_view)
    
    assert hasattr(controller, 'room_model') or hasattr(controller, 'model')
    assert hasattr(controller, 'view') or hasattr(controller, 'cli_view')


def test_schedule_controller_has_methods(config_model):
    """Test that ScheduleController has expected methods."""
    mock_view = Mock()
    controller = ScheduleController(config_model, mock_view)
    
    assert hasattr(controller, 'config_model') or hasattr(controller, 'model')
    assert hasattr(controller, 'view') or hasattr(controller, 'cli_view')


# ================================================================
# SMOKE TESTS: Controllers Accept Mock View
# ================================================================

def test_controllers_accept_mock_view(config_model):
    """Test that all controllers accept a Mock view without errors."""
    mock_view = Mock()
    
    # All of these should succeed
    faculty_model = FacultyModel(config_model)
    course_model = CourseModel(config_model)
    conflict_model = ConflictModel(config_model)
    lab_model = LabModel(config_model)
    room_model = RoomModel(config_model)
    
    controllers = [
        FacultyController(faculty_model, mock_view),
        CourseController(course_model, mock_view, config_model),  # Takes 3 params
        ConflictController(conflict_model, mock_view),
        LabController(lab_model, mock_view),
        RoomController(room_model, mock_view),
        ScheduleController(config_model, mock_view),
    ]
    
    # All should be instantiated
    assert len(controllers) == 6
    assert all(c is not None for c in controllers)